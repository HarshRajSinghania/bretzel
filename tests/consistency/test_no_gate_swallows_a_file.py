"""Gate : aucune gate ne fait sortir un fichier de son balayage en silence.

La gate qui garde les gates, deuxième du nom — sa sœur
``test_prohibition_gates_declare_a_floor`` garde « le balayage a-t-il
parlé ? », celle-ci garde « le balayage a-t-il tout lu ? ».

Le défaut qu'elle ferme
-----------------------
Le motif vivait dans **sept** fichiers de ce répertoire, à l'identique :

.. code-block:: python

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        continue          # ← le fichier sort du balayage, sans un mot

Ce n'était pas théorique. ``bretzel/render/__init__.py`` portait un BOM
UTF-8 — trois octets qu'``encoding="utf-8"`` laisse en tête de chaîne et
qu'``ast.parse`` refuse. Ce fichier était donc **hors du balayage de ces
sept gates**, et aucune ne le disait. Un fichier sur 344, pendant des
mois, pendant que les sept affichaient « zéro contrevenant ».

Une variante pire existait dans ``test_prose_matches_its_own_classvar``
: ``read_text(errors="ignore")``, qui ne saute pas le fichier mais MANGE
les octets qu'il ne sait pas décoder — donc peut couper une prose au
milieu de la citation qu'on cherche, sans que rien ne dépasse.

Ce que la gate exige
---------------------
Un balayage de fichiers passe par ``_discovery.parsed_sources()``, qui
lit en ``utf-8-sig`` et **lève** sur un fichier illisible. Le motif
``except …: continue`` autour d'une lecture ou d'un parse n'est donc plus
seulement découragé, il est refusé — et ``errors="ignore"`` avec lui.

Le même silence, à l'import
----------------------------
Une gate qui IMPORTE les modules qu'elle balaie perd pareil un module
qui ne s'importe pas. ``test_one_zone_per_table`` le faisait sous un
``except Exception: continue`` — et sous ``pytest -n``, un échec qui ne
frappe qu'un worker (une base SQLite recréée par un voisin) lui fait
collecter une autre liste que les autres : xdist refuse alors toute la
suite, en désignant des identifiants innocents (mesuré le 2026-09-26).
Un ``except Exception`` ou ``BaseException`` muet autour d'un
``import_module`` est donc refusé aussi.

Ce qu'elle ne peut PAS attraper
--------------------------------
Un ``except`` qui journalise puis continue (elle ne cherche que le corps
vide), et un balayage qui filtre trop en amont — un ``rglob`` sur un
sous-répertoire trop étroit lit tout ce qu'il voit, il voit juste trop
peu. C'est le travail du plancher, pas le sien.

Ni un ``except ImportError: continue`` autour d'un import : c'est la
forme d'une question légitime (« ce composant a-t-il un module de
thème ? », « quel est le plus long préfixe importable ? »), mais elle
avale aussi un ``ImportError`` levé À L'INTÉRIEUR du module sondé.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.consistency._discovery import (
    called_names,
    except_names,
    is_silent_handler,
)

#: Preuve de morsure : il fabrique les motifs exacts interdits (un
#: ``except … : continue`` autour d'un ``read_text`` ou d'un
#: ``import_module``) et leurs jumeaux licites, et les passe au détecteur.
MUTATION_PROOF = "test_sweep_is_not_vacuous"

_GATES_DIR = Path(__file__).resolve().parent

#: Ce qu'on rattrape quand on lit ou parse un fichier. Un ``except`` qui
#: nomme l'un d'eux ET dont le corps est vide fait disparaître un fichier.
_FILE_READ_ERRORS = frozenset({
    "SyntaxError", "UnicodeDecodeError", "UnicodeError", "OSError",
    "IOError", "FileNotFoundError",
})

#: ``_discovery`` EST l'implémentation autorisée : c'est le seul endroit
#: où le motif a le droit d'exister, et il y est suivi d'un ``assert`` qui
#: remonte les échecs au lieu de les taire.
_ALLOWED_FILES = frozenset({"_discovery.py"})

#: ``ast.literal_eval`` sur une valeur citée dans de la prose n'est PAS une
#: lecture de fichier : échouer y signifie « ce n'est pas un littéral »,
#: et passer au suivant est la bonne réponse. On distingue par le nom de
#: ce qui est appelé dans le ``try``, pas par le type rattrapé.
_VALUE_PARSERS = frozenset({"literal_eval", "tokenize"})


#: Ce qu'on rattrape quand on IMPORTE un module pour le balayer.
#: ``ImportError`` n'y est pas : cf. « Ce qu'elle ne peut PAS attraper ».
_IMPORT_SWALLOWERS = frozenset({"Exception", "BaseException"})

#: ``(appels qui chargent l'objet balayé, exceptions qui le font taire)``.
_SWALLOWED = (
    (frozenset({"parse", "read_text", "open", "read_bytes"}), _FILE_READ_ERRORS),
    (frozenset({"import_module"}), _IMPORT_SWALLOWERS),
)


def _gate_files() -> list[Path]:
    return sorted(
        p for p in _GATES_DIR.glob("*.py")
        if p.name not in _ALLOWED_FILES and not p.name.startswith("__")
    )


def _silent_skips(tree: ast.AST) -> list[str]:
    """Les ``except`` muets autour d'une lecture ou d'un import — le détecteur."""
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        called = called_names(node)
        if called & _VALUE_PARSERS:
            continue
        for loaders, swallowers in _SWALLOWED:
            # Un ``try`` qui ne charge rien de balayé ne nous regarde pas.
            if not called & loaders:
                continue
            offenders += [
                f"ligne {handler.lineno}"
                for handler in node.handlers
                if except_names(handler) & swallowers and is_silent_handler(handler)
            ]
    return offenders


@pytest.mark.parametrize("path", _gate_files(), ids=lambda p: p.name)
def test_no_silent_skip_on_unreadable_file(path: Path) -> None:
    offenders = _silent_skips(ast.parse(path.read_text(encoding="utf-8-sig")))
    assert not offenders, (
        f"{path.name} fait sortir un fichier de son balayage sans un mot "
        f"({', '.join(offenders)}). Un fichier illisible qui disparaît est "
        f"la même maladie qu'une gate vacuous : le plancher vérifie « le "
        f"balayage a parlé », jamais « le balayage a tout lu ». C'est un "
        f"BOM UTF-8 sur bretzel/render/__init__.py qui a fait sortir ce "
        f"fichier du balayage de SEPT gates pendant des mois.\n\n"
        f"Utilise ``_discovery.parsed_sources(root, floor=…)`` : elle lit "
        f"en utf-8-sig et LÈVE sur un fichier illisible. Pour un import, "
        f"accumule les échecs et ``assert`` à la fin, comme elle."
    )


@pytest.mark.parametrize("path", _gate_files(), ids=lambda p: p.name)
def test_no_gate_reads_with_errors_ignored(path: Path) -> None:
    """``errors="ignore"`` ne saute pas le fichier — il le MUTILE.

    Pire que le saut, parce qu'il ne laisse aucune trace : les octets
    indécodables disparaissent de la chaîne, et le balayage cherche son
    motif dans un texte qui n'est plus celui du fichier.
    """
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    bad: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
        if name not in ("read_text", "open", "decode"):
            continue
        for kw in node.keywords:
            if (
                kw.arg == "errors"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value in ("ignore", "replace")
            ):
                bad.append(node.lineno)
    assert not bad, (
        f"{path.name} lit avec ``errors={{'ignore'|'replace'}}`` "
        f"(ligne(s) {bad}). Les octets indécodables disparaissent en "
        f"silence, donc le balayage cherche son motif dans un texte qui "
        f"n'est plus celui du fichier. Lis en ``utf-8-sig`` — le seul cas "
        f"réel qu'``errors=`` absorbait ici était un BOM."
    )


def test_sweep_is_not_vacuous() -> None:
    """Plancher : on lit de vraies gates, et le motif reste détectable.

    Le second temps est le point délicat. Les deux tests ci-dessus sont
    des INTERDICTIONS : ils passeraient tout aussi bien si ``called_names``
    cessait de reconnaître quoi que ce soit. On vérifie donc sur des
    échantillons fabriqués que LE détecteur — ``_silent_skips``, celui
    que la gate appelle, pas une copie — mord encore, et qu'il épargne
    les jumeaux licites.
    """
    files = _gate_files()
    assert len(files) >= 40, (
        f"Seulement {len(files)} gates balayées dans {_GATES_DIR} — la "
        f"découverte est cassée."
    )

    def skips(body: str, handler: str) -> list[str]:
        return _silent_skips(ast.parse(
            f"for p in paths:\n    try:\n        {body}\n"
            f"    {handler}\n        continue\n"
        ))

    read = "t = ast.parse(p.read_text(encoding='utf-8'))"
    load = "m = importlib.import_module(p)"
    assert skips(read, "except SyntaxError:"), "lecture muette non vue"
    assert skips(load, "except Exception:"), "import muet non vu"
    assert skips(load, "except:"), "import muet sous ``except:`` nu non vu"
    # Les jumeaux licites : sonder l'existence d'un module, et un
    # ``except`` qui ne vise pas une erreur de lecture.
    assert not skips(load, "except ImportError:"), "faux positif sur la sonde"
    assert not skips(read, "except KeyError:"), "faux positif hors lecture"
