"""Gate : une chaîne traduite se résout à la requête, jamais à l'import.

``tr(en, fr)`` lit :class:`bretzel.Language` — la langue de LA REQUÊTE.
Appelé là où Python évalue une seule fois, il ne voit aucune requête et
rend l'anglais, pour toujours, à tout le monde. Rien ne lève et rien ne
rougit : la page rend, simplement dans la mauvaise langue.

Mesuré le 2026-09-26 sur ``examples/docs``, alors bilingue : **174
appels** gelés, dans 22 fichiers — le sommaire, les titres de page et les
tables de cinq chapitres. La doc est depuis en anglais seul ; la gate
garde les apps qui restent bilingues (``examples/kanban``).

Quatre endroits évaluent une fois, et la gate les refuse tous :

- le **niveau module** (une constante, une boucle) ;
- le **corps d'une classe**, exécuté à sa définition ;
- un **décorateur** — ``@page(title=tr(…))`` fige le ``<title>`` ; la
  forme par requête est ``ui.title(tr(…))`` dans la page ;
- un **défaut d'argument**, évalué à la définition de la fonction.

Et un cinquième, qui gèle à la PREMIÈRE requête au lieu de l'import :
un appel direct dans une fonction **mise en cache** (``lru_cache``,
``cache``). Le premier visiteur y choisit la langue de tous les autres.

Le même piège, côté framework, est gardé pour ``text()`` dans un
``reactive_prop(default=…)`` par
``test_framework_words_go_through_the_table``.

Ce que la gate ne voit pas
--------------------------
Elle lit l'appel, pas le flot. Une constante de module qui appelle une
FONCTION qui appelle ``tr()`` lui échappe, comme un cache posé deux
crans au-dessus.
"""

from __future__ import annotations

import ast
import functools
from pathlib import Path
from typing import Final

from tests.consistency._discovery import EXAMPLES_FLOOR, REPO_ROOT, parsed_sources

EXAMPLES_DIR: Final[Path] = REPO_ROOT / "examples"

#: Le nom de l'aide de traduction. Chaque app bilingue écrit la sienne
#: (``examples/kanban/core/i18n.py``) ;
#: ``test_the_translation_helper_is_watched`` vérifie que ce nom désigne
#: toujours des définitions réelles, sans quoi la gate serait vide sans
#: le dire.
_HELPER: Final[str] = "tr"

#: Les décorateurs qui mémorisent un résultat. Lus sur leur dernier
#: segment, pour attraper ``functools.lru_cache`` comme ``lru_cache``.
_CACHES: Final[frozenset[str]] = frozenset({"lru_cache", "cache"})


def _is_cached(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for deco in fn.decorator_list:
        target = deco.func if isinstance(deco, ast.Call) else deco
        name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
        if name in _CACHES:
            return True
    return False


def translation_calls(tree: ast.AST) -> list[tuple[int, bool]]:
    """Chaque appel à l'aide : ``(ligne, résolu_par_requête)``.

    Un appel est résolu par requête s'il est dans le CORPS d'une fonction
    (ou d'une lambda) non mise en cache. Les décorateurs et les défauts
    d'argument appartiennent à la portée qui ENTOURE la fonction : c'est
    là qu'ils s'évaluent.
    """
    out: list[tuple[int, bool]] = []

    def visit(node: ast.AST, per_request: bool) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            args = node.args
            for outer in [*args.defaults, *(d for d in args.kw_defaults if d)]:
                visit(outer, per_request)
            if isinstance(node, ast.Lambda):
                visit(node.body, True)
                return
            for deco in node.decorator_list:
                visit(deco, per_request)
            body_per_request = not _is_cached(node)
            for stmt in node.body:
                visit(stmt, body_per_request)
            return
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == _HELPER):
            out.append((node.lineno, per_request))
        for child in ast.iter_child_nodes(node):
            visit(child, per_request)

    visit(tree, False)
    return out


@functools.cache
def calls_by_file() -> dict[str, list[tuple[int, bool]]]:
    """Une passe, partagée par les tests. Le pré-filtre texte évite de
    descendre dans les ~250 fichiers qui n'appellent pas l'aide."""
    return {
        s.path.relative_to(EXAMPLES_DIR).as_posix(): translation_calls(s.tree)
        for s in parsed_sources(EXAMPLES_DIR, floor=EXAMPLES_FLOOR)
        if f"{_HELPER}(" in s.text
    }


def test_the_translation_helper_is_watched() -> None:
    """Le versant qui empêche la gate d'être vide : l'aide existe, et le
    détecteur en voit les appels. Mesuré le 2026-09-26 : 144 appels,
    tous dans ``examples/kanban``. Un renommage de ``tr`` ferait tomber ce compte à zéro, et
    « zéro appel gelé » se lirait comme « tout est propre »."""
    defined = [s.path for s in parsed_sources(EXAMPLES_DIR, floor=EXAMPLES_FLOOR)
               if any(isinstance(n, ast.FunctionDef) and n.name == _HELPER
                      for n in s.tree.body)]
    assert defined, f"l'aide `{_HELPER}` n'est plus définie nulle part dans examples/"
    seen = sum(len(calls) for calls in calls_by_file().values())
    assert seen >= 100, f"seulement {seen} appels à `{_HELPER}` vus dans examples/"


def test_no_translation_is_frozen() -> None:
    frozen = [f"{path}:{line}"
              for path, calls in calls_by_file().items()
              for line, per_request in calls if not per_request]
    assert not frozen, (
        f"{len(frozen)} appel(s) à `{_HELPER}()` s'évaluent une seule fois — "
        "à l'import ou au premier passage d'un cache — donc hors de la "
        "requête dont ils devraient lire la langue :\n  "
        + "\n  ".join(frozen)
        + "\n\nUne table traduite devient une FONCTION appelée au rendu "
        "(cf. `colonnes()` dans examples/kanban) ; un titre de page passe de "
        "`@page(title=tr(…))` à `ui.title(tr(…))` dans la page ; un défaut "
        "d'argument devient `None`, résolu dans le corps."
    )


def _frozen_in(source: str) -> list[int]:
    return [line for line, per_request in translation_calls(ast.parse(source))
            if not per_request]


def test_the_detector_still_bites() -> None:
    """Les deux versants : chaque forme gelée est vue, et chaque jumelle
    licite est épargnée."""
    frozen = {
        "constante": "X = tr('a', 'b')\n",
        "corps de classe": "class C:\n    x = tr('a', 'b')\n",
        "décorateur": "@page('/', title=tr('a', 'b'))\ndef p():\n    pass\n",
        "défaut": "def f(label=tr('a', 'b')):\n    pass\n",
        "défaut de lambda": "g = lambda label=tr('a', 'b'): label\n",
        "cache": "@lru_cache(maxsize=None)\ndef f():\n    return tr('a', 'b')\n",
        "cache qualifié": "@functools.cache\ndef f():\n    return tr('a', 'b')\n",
    }
    for form, source in frozen.items():
        assert _frozen_in(source), f"la forme gelée « {form} » n'est plus vue"

    licit = {
        "corps de fonction": "def f():\n    return tr('a', 'b')\n",
        "corps de lambda": "g = lambda: tr('a', 'b')\n",
        "fonction imbriquée": "def f():\n    def g(x=tr('a', 'b')):\n        pass\n",
        "méthode homonyme": "X = obj.tr('a', 'b')\n",
    }
    for form, source in licit.items():
        assert not _frozen_in(source), f"la forme licite « {form} » est refusée"
