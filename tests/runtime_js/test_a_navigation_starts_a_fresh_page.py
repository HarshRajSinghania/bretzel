"""Gate : dans un navigateur, une navigation boostée repart d'une page neuve.

Le trajet que ``tests/integration/server/test_a_navigation_starts_a_fresh_page.py``
ne peut pas faire : le PONT doit adopter l'identifiant que la navigation
renvoie. Sans lui, la page affichée est neuve mais l'action suivante
parle encore pour la page quittée — elle retrouve son vieil état, et le
compteur saute de 2 à 3 au lieu de repartir de 1.

C'est aussi la première gate qui NAVIGUE : les suites montaient une page
et s'arrêtaient, donc tout ce qui survit à un hx-boost leur échappait.

Run : ``py -m pytest tests/runtime_js/test_a_navigation_starts_a_fresh_page.py -q -m browser``
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, layout, page, refreshable, ui
from bretzel.probe import Window, probe
from bretzel.state import PageState, field

pytestmark = pytest.mark.browser


class Compteur(PageState):
    n: int = field(default=0)


class Vue(PageState):
    fil: str = field(default="")

    URL = {"fil": "c"}


def plus() -> None:
    Compteur().n += 1


@refreshable(deps=[Compteur, Vue])
def etat() -> None:
    ui.text(f"n={Compteur().n} fil=[{Vue().fil}]")


@layout
def coque() -> None:
    """Une coque à ``outlet`` : la navigation est PARTIELLE, le cas réel."""
    with ui.vstack():
        ui.link("accueil", href="/", attrs={"id": "vers-accueil"})
        ui.link("autre", href="/autre", attrs={"id": "vers-autre"})
        ui.outlet()


@page("/", title="accueil", layout=coque)
def accueil() -> None:
    ui.button("plus", id="plus", on_click=plus)
    etat()


@page("/autre", title="autre", layout=coque)
def autre() -> None:
    ui.text("ailleurs", attrs={"id": "ailleurs"})


APP = Bretzel(secret_key="f" * 32, mode="dev")
APP.include(__name__)

ZONE = "[data-bz-zone]"


def _etat(w: Window) -> str:
    return w.text(ZONE)


def test_a_boosted_navigation_starts_a_fresh_page() -> None:
    with probe(APP) as p:
        (a,) = p.windows
        a.goto("/?c=X")
        a.click("#plus")
        p.settle()
        a.click("#plus")
        p.settle()
        p.check("deux clics cumulent sur la même page", _etat(a) == "n=2 fil=[X]",
                _etat(a))

        a.click("#vers-autre")
        p.settle()
        a.page.wait_for_selector("#ailleurs")
        a.click("#vers-accueil")
        p.settle()
        p.check("revenir par un lien repart d'une page neuve",
                _etat(a) == "n=0 fil=[]", _etat(a))

        a.click("#plus")
        p.settle()
        p.check("et l'action suivante parle pour la page affichée",
                _etat(a) == "n=1 fil=[]",
                f"{_etat(a)} — n=3 voudrait dire l'id de la page quittée")
