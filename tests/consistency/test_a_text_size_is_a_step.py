"""Aucune taille de texte littérale dans le framework : un texte prend un palier.

Pourquoi cette gate existe
--------------------------
La densité de Bretzel se règle par la BASE de l'échelle
(``Theme(text=…)``, ``DEFAULT_TEXT``) : ``text-xs`` vaut 11 px par
défaut, et ce que l'app déclare sinon. Une chaîne qui écrit
``text-[10px]`` est hors de portée de ce réglage — elle ne bouge pas
quand la base bouge.

Il y en avait **31** dans les thèmes de composant le 2026-09-27 (badge,
avatar, calendar, select, combobox, tabs, pagination…), toutes au palier
``xs`` ou dans un sous-texte, et ``tokens.py`` les tenait pour une dette
connue (« hors de portée d'un jeton »). Mesurées sur l'atelier du
cockpit, elles donnaient la sixième taille de texte d'un même écran : 10 px
sous un minimum de 11. Elles sont toutes passées à ``text-xs``, et la
gate empêche la suivante.

⚠️ Le détecteur vise une taille EN VALEUR (``text-[10px]``,
``text-[0.8rem]``) : ``text-(--bz-text)`` est une couleur de palier et
``text-[#fff]`` une couleur littérale, deux autres sujets.
"""

from __future__ import annotations

import re

import pytest

from tests.consistency._discovery import (
    PACKAGE_DIR,
    PACKAGE_FLOOR,
    REPO_ROOT,
    code_string_literals,
    parsed_sources,
)

_LITERAL_TEXT_SIZE = re.compile(r"(?<![\w-])text-\[\d")


def offenders() -> list[str]:
    """``parsed_sources(floor=…)`` porte le plancher de non-vacuité ; le
    texte brut écarte d'abord les fichiers sans motif (l'AST ne sert qu'à
    ne pas compter un commentaire ou une docstring)."""
    return [
        f"{s.path.relative_to(REPO_ROOT)}:{node.lineno} — {node.value[:70]!r}"
        for s in parsed_sources(PACKAGE_DIR, floor=PACKAGE_FLOOR)
        if _LITERAL_TEXT_SIZE.search(s.text)
        for node in code_string_literals(s.tree)
        if _LITERAL_TEXT_SIZE.search(node.value)
    ]


def test_no_text_size_is_written_in_pixels() -> None:
    found = offenders()
    assert not found, (
        "taille de texte littérale dans le framework :\n  "
        + "\n  ".join(found)
        + "\n\nPrends un palier (text-xs … text-xl) : il suit Theme(text=…), "
        "un littéral ne suit rien."
    )


@pytest.mark.parametrize(
    "value, bites",
    [
        # Le versant INTERDIT.
        ("px-1.5 py-0 text-[10px] h-4", True),
        ("text-[0.8rem] leading-none", True),
        ("sm:text-[11px]", True),
        # Le versant LICITE — celui qui trouve les bugs de gate.
        ("text-xs", False),
        ("text-(--bz-text)", False),
        ("text-[#fff]", False),
        ("text-[length:var(--x)]", False),
        ("context-[10px]", False),
    ],
)
def test_the_detector_still_bites(value: str, bites: bool) -> None:
    assert bool(_LITERAL_TEXT_SIZE.search(value)) is bites
