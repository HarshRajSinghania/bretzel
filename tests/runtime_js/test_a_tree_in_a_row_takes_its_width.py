"""``ui.tree`` dans une rangée prend la largeur de ses nœuds.

Ce que ça ferme, mesuré le 2026-09-29
--------------------------------------
La racine portait ``w-full`` : dans un ``hstack``, l'arbre prenait toute
la ligne et écrasait son voisin, et ``classes="w-60"`` ne gagnait pas de
façon fiable — deux utilitaires de largeur au même niveau de
spécificité, départagés par l'ordre de la feuille (traps.md).

Mesure préalable sur les onze apps d'exemple (214 pages, 30 arbres
visibles) : retirer ``w-full`` n'en change qu'un, celui d'une rangée
centrée du playground, et dans le bon sens. Dans une pile ou un bloc, la
racine ``flex`` reste de niveau bloc et remplit toujours sa colonne —
c'est le versant licite, mesuré ici aussi.

Lourd (uvicorn + Chromium) ::

    py -m pytest tests/runtime_js/test_a_tree_in_a_row_takes_its_width.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

app = Bretzel(secret_key="a" * 32, title="arbre", mode="dev")


def arbre(**kwargs) -> None:
    with ui.tree(**kwargs), ui.tree_node("src", label="src", icon="folder"):
        ui.tree_node("main.py", label="main.py", icon="file-code")


@page("/")
def home() -> None:
    with ui.vstack(gap="lg", classes="p-6 w-[48rem]"):
        # Enfant DIRECT de la rangée : une pile intermédiaire, elle-même
        # dimensionnée sur son contenu, masquerait le ``w-full``.
        with ui.hstack(gap="sm", align="start", id="rangee"):
            arbre(id="rangee-arbre")
            ui.button("Voisin", id="voisin")
        with ui.hstack(gap="sm", align="start"):
            arbre(id="arbre-fixe", classes="w-60")
        with ui.vstack(id="pile"):
            arbre(id="arbre-pile")


app.include(__name__)

MEASURE = r"""() => {
  const box = (sel) => document.querySelector(sel).getBoundingClientRect();
  const tree = (id) => box('#' + id);
  const probe = document.createElement('div');
  probe.className = 'w-60';
  document.body.appendChild(probe);
  const w60 = probe.getBoundingClientRect().width;
  probe.remove();
  return {
    row: box('#rangee').width,
    tree: tree('rangee-arbre').width,
    neighbourGap: box('#voisin').left - tree('rangee-arbre').right,
    fixed: tree('arbre-fixe').width,
    w60,
    stack: box('#pile').width,
    stackTree: tree('arbre-pile').width,
  };
}"""


@pytest.fixture(scope="module")
def mesure():
    with audit_server(app) as url, browser_page(url, "/") as pg:
        pg.wait_for_selector("html.bz-ready", state="attached")
        pg.wait_for_timeout(300)
        yield pg.evaluate(MEASURE)


def test_the_page_is_measured(mesure) -> None:
    assert mesure["row"] > 500 and mesure["tree"] > 20 and mesure["w60"] > 100, mesure


def test_a_tree_in_a_row_leaves_room_for_its_neighbour(mesure) -> None:
    assert mesure["tree"] < mesure["row"] / 2 and mesure["neighbourGap"] < 40, (
        f"l'arbre mesure {mesure['tree']:.0f} px dans une rangée de "
        f"{mesure['row']:.0f} px, son voisin est à {mesure['neighbourGap']:.0f} px : "
        f"il prend toute la ligne."
    )


def test_a_width_class_wins(mesure) -> None:
    assert abs(mesure["fixed"] - mesure["w60"]) < 1, (
        f"classes='w-60' donne {mesure['fixed']:.0f} px au lieu de "
        f"{mesure['w60']:.0f} : une largeur du thème lui dispute la place."
    )


def test_a_tree_in_a_stack_still_fills_it(mesure) -> None:
    """Le versant licite."""
    assert mesure["stackTree"] > mesure["stack"] - 2, mesure
