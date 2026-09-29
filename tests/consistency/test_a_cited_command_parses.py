"""Gate : une commande ``bretzel …`` citée dans la prose passe le vrai parseur.

Le défaut qu'elle ferme
-----------------------
L'indice de la règle ``unknown-kwarg`` conseillait ``bretzel describe
--index`` — une option que ``build_parser()`` n'a jamais eue (réparé au
commit 8d5b56e4). Rien ne relisait les commandes citées : la prose les
enseigne, une IA les recopie telles quelles, le parseur les refuse.

Le jour de sa livraison, elle en a trouvé cinq autres, de deux sortes :

- ``bretzel build`` (trois fois), une sous-commande qui n'a jamais
  existé, citée par deux docstrings et surtout par le commentaire du
  ``style.css`` vide — servi au navigateur, et qui disait de la lancer ;
- ``describe bretzel --depth 1`` (deux fois) dans la docstring de
  ``render_tree`` : la CLI n'a pas de ``--depth``, et ``render_tree``
  n'a aucun appelant.

Ce qu'elle lit
--------------
Les spans entre backticks — simples ou doubles, une coupure de ligne
admise — qui commencent par ``bretzel <sous-commande>``, ou par la
sous-commande seule suivie d'au moins un mot : c'est la forme de la tête
de l'index (``describe <name> [<name> …]``), la première chose qu'une IA
lit. Dans :

- ``bretzel/**/*.py`` : toutes les chaînes (docstrings, messages et
  indices des règles de lint) et les commentaires. Une f-string est lue
  RENDUE, chaque ``{expr}`` devenant un gabarit ;
- ``examples/docs/features/*.py``, la doc vivante ;
- ``README.md``, ``CLAUDE.md`` et ``.claude/bretzel/*.md``, où une ligne
  de bloc de code clôturé qui commence par ``bretzel`` compte aussi.

Un ``.py`` sans backtick suivi d'un mot de tête n'est pas marché : 33
fichiers sur 481 en portent, et marcher les autres coûtait une seconde.

Comment elle juge
-----------------
- ``bretzel <sous-commande>`` seul NOMME la commande : il est jugé comme
  ``bretzel <sous-commande> --help``, donc sur l'existence de la
  sous-commande. ``bretzel probe`` exige une cible, et la phrase qui le
  nomme n'est pas fausse pour autant.
- Avec des arguments, ``build_parser().parse_args()`` tranche : un
  ``SystemExit`` non nul est un contrevenant (``--help`` sort en 0).
- Les gabarits sont substitués : ``<x>``, ``{expr}``, ``module:attr`` ;
  un groupe ``[…]`` est essayé absent et présent ; ``…`` est retiré. Le
  TYPE d'un gabarit est inconnu (``--port <n>`` attend un entier), donc
  chacun essaie une chaîne, un entier et une taille, et la commande passe
  si une combinaison passe.
- Elle ne sait PAS juger un gabarit à la place de la sous-commande
  (``bretzel <command>``) ou d'un nom d'option (``--<flag>``), ni un span
  que ``shlex`` ne découpe pas. Ceux-là sont déclarés dans
  ``_UNJUDGEABLE`` avec leur raison, et la table refuse l'écart dans les
  deux sens.

Ce qu'elle ne peut PAS attraper
-------------------------------
- Qu'une commande qui parse MARCHE. ``describe --theme`` sans nom parse,
  puis sort en 2 ; ``describe nimporte_quoi`` parse, puis ne trouve rien.
  Elle juge la grammaire, pas la sémantique.
- Une commande hors backticks : le ``print("  bretzel dev")`` de
  ``bretzel new``, les blocs ``ui.code`` de la doc vivante, un
  ``.. code-block::`` de docstring, une invocation par
  ``py -m bretzel.cli.main``.
- ``new`` sans son préfixe : homonyme de l'opérateur JavaScript, il n'est
  lu qu'après ``bretzel`` (cf. ``_HOMONYMS``).
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import dataclasses
import functools
import io
import itertools
import re
import shlex
import tokenize
from collections.abc import Iterator
from pathlib import Path

from bretzel.cli.main import build_parser
from tests.consistency._discovery import (
    EXAMPLES_FLOOR,
    PACKAGE_DIR,
    PACKAGE_FLOOR,
    REPO_ROOT,
    ParsedSource,
    parsed_sources,
)

_DOCS_FEATURES = REPO_ROOT / "examples" / "docs" / "features"

#: Une sous-commande qui, SANS le préfixe ``bretzel``, désigne autre chose
#: dans le corpus. Elle n'est lue qu'après ``bretzel``.
_HOMONYMS: dict[str, str] = {
    "new": (
        "l'opérateur JavaScript — ``new Function`` (``runtime.md``, "
        "``security.md``), ``new Date()`` (le date_picker)."
    ),
}

#: Les commandes citées qu'elle ne sait pas juger, avec la raison pour
#: laquelle la phrase reste juste. Vide : aucune aujourd'hui.
_UNJUDGEABLE: dict[str, str] = {}

#: Ce qu'un gabarit peut valoir. Son TYPE est inconnu — ``<port>`` attend
#: un entier, ``<WxH>`` une taille, ``<app>`` une chaîne —, donc chacun
#: essaie les trois.
_FILLERS = ("app.main:app", "1", "1280x700")


# ── Le parseur ────────────────────────────────────────────────────────


@functools.lru_cache(maxsize=1)
def _parser() -> argparse.ArgumentParser:
    return build_parser()


@functools.lru_cache(maxsize=1)
def subcommands() -> frozenset[str]:
    """Les sous-commandes que le parseur connaît — lues sur LUI, pas
    recopiées : une sous-commande ajoutée est lue sans retoucher la gate."""
    groups = [
        action.choices for action in _parser()._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    assert len(groups) == 1, (
        f"{len(groups)} groupes de sous-commandes dans build_parser() — la "
        f"gate ne sait plus lesquelles existent."
    )
    return frozenset(groups[0])


def _complaint(argv: list[str]) -> str | None:
    """``None`` si le parseur accepte ``argv`` ; sa plainte sinon."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            _parser().parse_args(argv)
    except SystemExit as exc:
        if exc.code in (0, None):  # ``--help`` : une commande valide
            return None
        lines = err.getvalue().strip().splitlines()
        return lines[-1] if lines else f"code de sortie {exc.code}"
    return None


# ── Le détecteur ──────────────────────────────────────────────────────

#: Un span de code : N backticks, un contenu sans backtick ni ligne
#: blanche, les MÊMES N backticks. Une clôture de bloc n'ouvre ni ne
#: ferme rien : ses backticks sont collés.
_SPAN = re.compile(r"(?<!`)(`{1,2})(?!`)((?:(?!\n[ \t]*\n)[^`])+?)\1(?!`)")

#: La tête d'une commande : ``bretzel`` (facultatif), puis la
#: sous-commande — un mot, ou un gabarit qu'on ne saura pas juger.
_HEAD = re.compile(
    r"(?:(?P<prog>bretzel)\s+)?(?P<sub>[a-z][\w-]*|<[^<>]*>|\{[^{}]*\})(?=\s|$)"
)

_FENCE = re.compile(r"^[ \t]*```")
_PROMPT = re.compile(r"^\$\s+")

_OPTIONAL = re.compile(r"\[([^\[\]]*)\]")
_SLOT = re.compile(r"<[^<>]*>|\{[^{}]*\}|\bmodule:attr\b")
_ELLIPSIS = re.compile(r"(?<![^\s\[])(?:…|\.\.\.)(?=[\s\]]|$)")
#: Un gabarit à la place d'un NOM d'option : ``--<flag>``.
_OPTION_SLOT = re.compile(r"(?<!\S)-{1,2}(?=[<{])")
#: Ce qui termine la commande dans un span : ``| head``, ``&& cd …``.
_SHELL_OPERATORS = frozenset("();<>|&")


@functools.lru_cache(maxsize=1)
def _mention() -> re.Pattern[str]:
    """Le pré-filtre d'un fichier : un backtick suivi d'un mot de tête.

    Il ne doit rien écarter que :data:`_SPAN` et :data:`_HEAD` liraient —
    d'où ``new`` dedans, que la table des homonymes a besoin de voir."""
    words = "|".join(sorted({"bretzel"} | subcommands()))
    return re.compile(rf"`\s*(?:{words})\b")


def as_command(span: str) -> str | None:
    """Le span, espaces normalisés, s'il cite une commande ; ``None`` sinon."""
    text = " ".join(span.split())
    head = _HEAD.match(text)
    if head is None:
        return None
    if head["prog"]:
        return text
    # Sans préfixe : une vraie sous-commande, pas un homonyme, et au moins
    # un argument — ``describe`` seul est aussi la fonction Python.
    if head["sub"] in subcommands() - _HOMONYMS.keys() and head.end() < len(text):
        return text
    return None


def commands_in(text: str) -> list[tuple[int, str]]:
    """``(lignes avant le span, commande)`` pour chaque span qui en cite une."""
    out: list[tuple[int, str]] = []
    for match in _SPAN.finditer(text):
        command = as_command(match.group(2))
        if command is not None:
            out.append((text.count("\n", 0, match.start()), command))
    return out


@dataclasses.dataclass(frozen=True)
class Verdict:
    kind: str  # "ok" | "offender" | "unjudgeable"
    detail: str = ""


def _readings(rest: str) -> list[str]:
    """Toutes les lectures concrètes des arguments d'une commande."""
    rest = _ELLIPSIS.sub("", rest)
    optional = _OPTIONAL.search(rest)
    if optional is not None:
        before, after = rest[:optional.start()], rest[optional.end():]
        return (
            _readings(before + " " + after)
            + _readings(before + " " + optional.group(1) + " " + after)
        )
    slots = len(_SLOT.findall(rest))
    return [_fill(rest, values) for values in itertools.product(_FILLERS, repeat=slots)]


def _fill(text: str, values: tuple[str, ...]) -> str:
    """Chaque gabarit de ``text`` remplacé, dans l'ordre, par ``values``."""
    remaining = iter(values)
    return _SLOT.sub(lambda _slot: next(remaining), text)


def _argv(reading: str) -> list[str]:
    """Les mots d'une lecture, coupés au premier opérateur shell."""
    lexer = shlex.shlex(reading, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(itertools.takewhile(lambda t: not set(t) <= _SHELL_OPERATORS, lexer))


@functools.cache
def judge(command: str) -> Verdict:
    """Le verdict du parseur sur une commande citée."""
    head = _HEAD.match(command)
    assert head is not None, f"pas une commande : {command!r}"
    sub, rest = head["sub"], command[head.end():].strip()
    if sub[0] in "<{":
        return Verdict("unjudgeable", "un gabarit tient la place de la sous-commande")
    if _OPTION_SLOT.search(rest):
        return Verdict("unjudgeable", "un gabarit tient la place d'un nom d'option")
    # Sans argument, la commande est NOMMÉE, pas invoquée : on demande son
    # aide, qui sort en 0 si la sous-commande existe.
    try:
        argvs = [[sub, *_argv(reading)] for reading in _readings(rest or "--help")]
    except ValueError as exc:
        return Verdict("unjudgeable", f"shlex ne découpe pas le span : {exc}")
    complaints = [_complaint(argv) for argv in argvs]
    if None in complaints:
        return Verdict("ok")
    return Verdict("offender", str(complaints[0]))


# ── Le corpus ─────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class Citation:
    where: str  # ``chemin:ligne``
    text: str  # la commande, espaces normalisés
    fenced: bool = False  # une ligne de bloc de code clôturé


def python_prose(source: ParsedSource) -> Iterator[tuple[int, str]]:
    """``(ligne, texte)`` : chaque chaîne du module, puis chaque bloc de
    commentaires consécutifs.

    Une f-string est RENDUE, ``{expr}`` à la place de chaque valeur : lue
    morceau par morceau, ``f"`bretzel describe {func.attr}`"`` donnerait
    un span ouvert que rien ne ferme."""
    stack: list[ast.AST] = [source.tree]
    while stack:
        node = stack.pop()
        if isinstance(node, ast.JoinedStr):
            yield node.lineno, "".join(
                "{" + ast.unparse(part.value) + "}"
                if isinstance(part, ast.FormattedValue) else str(part.value)
                for part in node.values
            )
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value
        stack.extend(ast.iter_child_nodes(node))

    block: list[str] = []
    start = last = 0
    for token in tokenize.generate_tokens(io.StringIO(source.text).readline):
        if token.type != tokenize.COMMENT:
            continue
        line = token.start[0]
        if block and line != last + 1:
            yield start, "\n".join(block)
            block = []
        if not block:
            start = line
        block.append(token.string.lstrip("#:").strip())
        last = line
    if block:
        yield start, "\n".join(block)


def split_markdown(text: str) -> tuple[str, list[tuple[int, str]]]:
    """``(prose, lignes de blocs)``. Les blocs de code clôturés sont
    BLANCHIS dans la prose — ses numéros de ligne restent justes, et un
    backtick de code n'y apparie rien — et rendus à part, ligne à ligne."""
    prose: list[str] = []
    fenced: list[tuple[int, str]] = []
    inside = False
    for number, line in enumerate(text.splitlines(), start=1):
        if _FENCE.match(line):
            inside = not inside
            prose.append("")
        elif inside:
            prose.append("")
            fenced.append((number, _PROMPT.sub("", line.strip())))
        else:
            prose.append(line)
    return "\n".join(prose), fenced


def _python_sources() -> list[ParsedSource]:
    package = parsed_sources(PACKAGE_DIR, floor=PACKAGE_FLOOR)
    docs_app = [
        s for s in parsed_sources(REPO_ROOT / "examples", floor=EXAMPLES_FLOOR)
        if s.path.parent == _DOCS_FEATURES
    ]
    return package + docs_app


@functools.lru_cache(maxsize=1)
def _markdown() -> tuple[tuple[str, str, tuple[tuple[int, str], ...]], ...]:
    """``(fichier, prose, lignes de blocs)`` de la doc écrite à la main.

    ``.claude/work/`` n'y est pas : ce sont des rapports datés, qui citent
    la CLI telle qu'elle était à leur date."""
    paths = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "CLAUDE.md",
        *sorted((REPO_ROOT / ".claude" / "bretzel").glob("*.md")),
    ]
    out = []
    for path in paths:
        prose, fenced = split_markdown(path.read_text(encoding="utf-8-sig"))
        out.append((path.relative_to(REPO_ROOT).as_posix(), prose, tuple(fenced)))
    return tuple(out)


@functools.lru_cache(maxsize=1)
def prose_texts() -> tuple[tuple[str, int, str], ...]:
    """``(fichier, ligne, texte)`` — toute la prose balayée, blocs exclus."""
    out: list[tuple[str, int, str]] = []
    for source in _python_sources():
        if not _mention().search(source.text):
            continue
        label = source.path.relative_to(REPO_ROOT).as_posix()
        out += [(label, lineno, text) for lineno, text in python_prose(source)]
    out += [(label, 1, prose) for label, prose, _fenced in _markdown()]
    return tuple(out)


@functools.lru_cache(maxsize=1)
def citations() -> tuple[Citation, ...]:
    """Chaque commande citée, là où elle l'est."""
    out = [
        Citation(f"{label}:{lineno + offset}", command)
        for label, lineno, text in prose_texts()
        for offset, command in commands_in(text)
    ]
    for label, _prose, fenced in _markdown():
        out += [
            Citation(f"{label}:{number}", command, fenced=True)
            for number, line in fenced
            if line.startswith("bretzel ") and (command := as_command(line)) is not None
        ]
    return tuple(out)


def offenders() -> list[str]:
    return [
        f"{c.where} : `{c.text}` — {verdict.detail}"
        for c in citations()
        if (verdict := judge(c.text)).kind == "offender"
    ]


# ── Les planchers ─────────────────────────────────────────────────────
#
# Ils lisent la découverte de CETTE gate : un plancher qui recompte depuis
# son propre glob reste vert quand on débranche le balayage.


def test_the_sweep_is_not_vacuous() -> None:
    found = citations()
    assert len(found) >= 80, (
        f"seulement {len(found)} commandes citées trouvées — l'extracteur ou "
        f"le périmètre a cassé, la gate ne garde plus rien."
    )
    # Chaque périmètre doit mordre : sans ça, en débrancher un ferait
    # juste baisser un total qui reste au-dessus du plancher.
    lint = [c for c in found if c.where.startswith("bretzel/lint/rules/")]
    package = [c for c in found if c.where.startswith("bretzel/")]
    docs_app = [c for c in found if c.where.startswith("examples/docs/features/")]
    markdown = [c for c in found if ".md:" in c.where and not c.fenced]
    fenced = [c for c in found if c.fenced]
    assert len(lint) >= 4, f"indices des règles de lint : {len(lint)}"
    assert len(package) >= 50, f"paquet : {len(package)}"
    assert len(docs_app) >= 4, f"doc vivante : {len(docs_app)}"
    assert len(markdown) >= 15, f"markdown : {len(markdown)}"
    assert len(fenced) >= 4, f"blocs de code clôturés : {len(fenced)}"


def test_the_watched_forms_are_met() -> None:
    """Chaque FORME que le détecteur sait lire est rencontrée dans le corpus.

    Un plancher borne la population ; il ne dit rien de ce que le
    détecteur y reconnaît (``gates.md`` § « Une gate qui cherche un NOM
    peut être vide sans le dire »). Une branche morte — la tête sans
    préfixe, le rendu des f-strings — laisserait passer ses commandes en
    silence, pendant que le total resterait au-dessus du plancher.
    """
    texts = [c.text for c in citations()]
    forms = {
        "sans le préfixe bretzel": [t for t in texts if not t.startswith("bretzel ")],
        "gabarit <x>": [t for t in texts if "<" in t],
        "gabarit {expr} d'une f-string": [t for t in texts if "{" in t],
        "groupe facultatif [...]": [t for t in texts if _OPTIONAL.search(t)],
        "commande nommée, sans argument": [
            t for t in texts if t.startswith("bretzel ") and len(t.split()) == 2
        ],
        "avec une option": [t for t in texts if " --" in t],
    }
    missing = sorted(name for name, seen in forms.items() if not seen)
    assert not missing, (
        f"formes que le détecteur ne rencontre plus : {missing}. Soit la "
        f"prose a changé, soit la branche est morte — vérifie avant de "
        f"croire le vert."
    )


# ── L'interdiction ────────────────────────────────────────────────────


def test_every_cited_command_parses() -> None:
    bad = offenders()
    assert not bad, (
        f"{len(bad)} commande(s) citée(s) que la CLI refuse :\n  "
        + "\n  ".join(bad)
        + "\n\nUne commande écrite dans la prose est une consigne : une IA "
        "la recopie telle quelle. Corrige la phrase sur `bretzel <cmd> "
        "--help`, pas l'inverse — sauf si l'option manque vraiment, et "
        "alors c'est une décision d'API."
    )


def test_the_abstentions_are_declared() -> None:
    """Ce qu'elle ne sait pas juger est NOMMÉ — dans les deux sens."""
    measured = {c.text: verdict.detail for c in citations()
                if (verdict := judge(c.text)).kind == "unjudgeable"}
    undeclared = sorted(f"`{t}` — {why}" for t, why in measured.items()
                        if t not in _UNJUDGEABLE)
    stale = sorted(_UNJUDGEABLE.keys() - measured.keys())
    assert not undeclared, (
        "commandes citées que la gate ne sait pas juger, non déclarées :\n  "
        + "\n  ".join(undeclared)
        + "\n\nRends-les jugeables (un gabarit en position d'argument se "
        "substitue), ou déclare-les dans `_UNJUDGEABLE` AVEC la raison "
        "pour laquelle la phrase reste juste."
    )
    assert not stale, (
        f"entrées de `_UNJUDGEABLE` qui ne correspondent plus à rien : "
        f"{stale}. Retire-les, sinon la table pourrit."
    )


def test_a_homonym_is_still_needed() -> None:
    """Une entrée de ``_HOMONYMS`` nomme une vraie sous-commande, et le
    corpus cite encore l'homonyme qu'elle écarte."""
    assert not _HOMONYMS.keys() - subcommands(), (
        f"_HOMONYMS nomme des sous-commandes disparues : "
        f"{sorted(_HOMONYMS.keys() - subcommands())}"
    )
    met = {
        words[0]
        for _label, _lineno, text in prose_texts()
        for _ticks, span in _SPAN.findall(text)
        if (words := span.split())
    } & _HOMONYMS.keys()
    assert not _HOMONYMS.keys() - met, (
        f"plus aucun span ne commence par {sorted(_HOMONYMS.keys() - met)} : "
        f"l'homonyme a disparu du corpus, l'exclusion ne protège plus rien. "
        f"Retire l'entrée."
    )


# ── La preuve qu'elle mord ────────────────────────────────────────────


def _commands(prose: str) -> list[str]:
    return [command for _offset, command in commands_in(prose)]


def test_the_detector_still_bites() -> None:
    """Le versant qui MORD, sur les trois fautes réellement trouvées."""
    for prose, needle in (
        ("L'indice : lance `bretzel describe --index` pour les voir.", "--index"),
        ("once ``bretzel build`` runs, this serves the real bundle.", "invalid choice"),
        ("``describe bretzel --depth 1`` shows the big blocks.", "--depth"),
        ("`bretzel check --deep\n--strict <module:attr>`", "--strict"),
    ):
        commands = _commands(prose)
        assert len(commands) == 1, f"{prose!r} : {commands}"
        verdict = judge(commands[0])
        assert verdict.kind == "offender" and needle in verdict.detail, (
            f"{prose!r} n'est pas refusée : {verdict}"
        )


def test_the_detector_spares_a_real_command() -> None:
    """Le versant LICITE — celui qui trouve les faux positifs."""
    for prose in (
        "Full details: `describe <name> [<name> …]` — every card, one call.",
        "`bretzel check --deep module:attr`",
        "`bretzel check <app>` sans constat, et `check --deep\n<module:attr>`",
        "`bretzel probe` et `bretzel new`",  # nommées, pas invoquées
        "`bretzel dev --port <port>`",  # un gabarit d'entier
        "`bretzel probe <app> --size <WxH>`",  # un gabarit de taille
        "`bretzel describe --help`",  # sort en 0
        "``bretzel describe button | head``",
        "`bretzel new <name> ...`",  # l'ellipse ASCII n'est pas un argument
    ):
        commands = _commands(prose)
        assert commands, f"{prose!r} : aucune commande lue"
        judged = {c: judge(c) for c in commands}
        assert all(v.kind == "ok" for v in judged.values()), judged

    # La f-string est lue RENDUE, et son ``{expr}`` est un gabarit.
    code = 'HINT = f"run `bretzel describe {func.attr}` to see it"\n'
    assert _mention().search(code), "le pré-filtre écarterait ce fichier"
    source = ParsedSource(Path("fabrique.py"), code, ast.parse(code))
    rendered = [c for _l, text in python_prose(source) for c in _commands(text)]
    assert rendered == ["bretzel describe {func.attr}"], rendered
    assert judge(rendered[0]).kind == "ok"

    # Une ligne de bloc clôturé est lue, sa prose d'à côté aussi.
    prose, fenced = split_markdown(
        "Lance `bretzel dev`.\n```bash\n$ bretzel dev app.main:app --port 8010\n```\n"
    )
    assert _commands(prose) == ["bretzel dev"]
    assert fenced == [(3, "bretzel dev app.main:app --port 8010")]
    assert judge(as_command(fenced[0][1]) or "").kind == "ok"

    # Ce qui n'est pas une commande n'est pas lu.
    assert not _commands(
        "`new Function`, `bretzel.state`, `bretzel`, `describe`, `describe(name)`"
    )


def test_the_detector_says_what_it_cannot_judge() -> None:
    """Le troisième verdict existe, et il n'est ni un vert ni un rouge."""
    for prose in (
        "`bretzel <command> --help`",
        "`bretzel check --<flag>`",
        "`bretzel new \"sans guillemet fermant`",
    ):
        commands = _commands(prose)
        assert len(commands) == 1, f"{prose!r} : {commands}"
        assert judge(commands[0]).kind == "unjudgeable", (
            f"{prose!r} : {judge(commands[0])}"
        )
