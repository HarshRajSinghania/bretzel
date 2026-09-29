"""Gate : chaque symbole ``ui.*`` est montré dans la vitrine.

``examples/showcase`` est la face publique du catalogue — une page par
composant, des usages réels et leur code. Sa promesse est « tous les
composants », et c'est une promesse qui dérive seule : un composant
ajouté au framework n'a aucune raison de trouver sa page si rien ne le
réclame. La vitrine resterait verte, belle, et incomplète, ce qui est
exactement ce qu'un visiteur ne verra jamais.

La découverte lit le namespace ``ui`` lui-même (``ui_symbol_names``,
composants ET helpers), pas une liste écrite ici : le prochain symbole
public est réclamé sans qu'on touche ce fichier.

Ce qui compte comme « montré » : un APPEL ``ui.<nom>`` dans le code de la
vitrine, lu dans l'AST — ses pages, et sa coque : ``ui.outlet`` n'a de sens
que dans un layout, et c'est celui de la vitrine qui le montre (la page
*Page utilities* affiche son code). Une mention en texte, en
docstring ou en commentaire ne compte pas — elle ne rend rien.
"""

from __future__ import annotations

import ast
from pathlib import Path

from bretzel.introspect.components import ui_symbol_names
from tests.consistency._discovery import parsed_sources

SHOWCASE_DIR = Path(__file__).resolve().parents[2] / "examples" / "showcase"

#: Mesuré à la création (2026-09-29) : 92 fichiers (77 pages), 114 symboles.
_FILES_FLOOR = 85
_SYMBOLS_FLOOR = 100


def called_ui_names(tree: ast.AST) -> set[str]:
    """Les ``ui.<nom>`` APPELÉS dans un arbre — le détecteur de la gate."""
    return {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "ui"
    }


def shown() -> set[str]:
    return set().union(*(
        called_ui_names(source.tree)
        for source in parsed_sources(SHOWCASE_DIR, floor=_FILES_FLOOR)
    ))


def test_the_sweep_is_not_vacuous() -> None:
    assert len(ui_symbol_names()) >= _SYMBOLS_FLOOR, (
        f"le namespace `ui` n'expose plus que {len(ui_symbol_names())} "
        f"symboles — la découverte est cassée, pas la vitrine."
    )
    assert len(shown()) >= _SYMBOLS_FLOOR, (
        f"les pages de la vitrine n'appellent que {len(shown())} symboles "
        f"`ui.*` — le détecteur ne lit plus les appels."
    )


def test_every_ui_symbol_is_shown() -> None:
    missing = sorted(set(ui_symbol_names()) - shown())
    assert not missing, (
        f"{len(missing)} symbole(s) `ui.*` sans usage dans la vitrine : "
        f"{missing}.\n  Ajoute un exemple dans la page de sa famille "
        f"(`examples/showcase/features/components/`), ou une page et sa "
        f"ligne dans `examples/showcase/app/catalog.py`."
    )


def test_the_detector_still_bites() -> None:
    seen = called_ui_names(ast.parse(
        "ui.button('Save')\n"
        "with ui.tabs(value='a'):\n    ui.tab('a')\n"
    ))
    assert seen == {"button", "tabs", "tab"}
    # Le versant qui épargne : une mention n'est pas un usage.
    assert not called_ui_names(ast.parse(
        "'''Uses ui.select.'''\n# ui.dialog(...)\nx = 'ui.drawer()'\nf = ui.card\n"
    ))
