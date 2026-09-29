"""Une fermeture RAPPORTÉE au serveur laisse le rendu suivant décider.

Le × d'un ``ui.badge`` / ``ui.alert`` / ``ui.banner`` pose ``open = false``
dans un scope ``bz-data`` local, que ``absorb`` ne réécrit jamais. Sans
``key=``, l'identité d'un élément d'une boucle est sa POSITION : quand
``on_close`` retire la puce « Alpha » et que la zone se re-rend, « Bravo »
hérite de ``chips_badge_0`` — et du ``open: false`` d'Alpha. Mesuré le
2026-09-29 dans la vitrine : la puce suivante disparaît avec celle qu'on
ferme, et « Reset » rend Alpha invisible.

Quand un handler SERVEUR reçoit la fermeture, c'est lui qui décide de
l'existence de la puce ; le rendu qu'il déclenche fait donc foi, et
``open`` est re-semé (``_serverSync``). Sans handler serveur, la
fermeture reste une affaire du navigateur : un refresh voisin ne
ressuscite pas une puce fermée (le versant licite, testé aussi).

Lourd (uvicorn + Chromium) ::

    py -m pytest tests/runtime_js/test_a_reported_dismiss_follows_the_server.py -q -m browser
"""

from __future__ import annotations

import functools

import pytest

from bretzel import Bretzel, page, refreshable, ui
from bretzel.state import PageState, field
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

app = Bretzel(
    secret_key="dev-reported-dismiss-secret-key-xxxxxx",
    title="Bretzel · fermeture rapportée",
    mode="dev",
)


def default_chips() -> list[str]:
    return ["Alpha", "Bravo", "Charlie"]


class Chips(PageState):
    active: list[str] = field(default_factory=default_chips)
    ticks: int = field(default=0)


def remove_chip(label: str) -> None:
    chips = Chips()
    chips.active = [c for c in chips.active if c != label]


def reset_chips() -> None:
    Chips().active = default_chips()


def tick() -> None:
    Chips().ticks += 1


@refreshable(deps=[Chips])
def reported() -> None:
    with ui.hstack(gap="sm", id="reported"):
        for label in Chips().active:
            ui.badge(label, on_close=functools.partial(remove_chip, label))


@refreshable(deps=[Chips])
def local() -> None:
    with ui.hstack(gap="sm", id="local"):
        ui.text(f"ticks = {Chips().ticks}", id="ticks")
        ui.badge("Local", dismissible=True)


@page("/")
def home() -> None:
    with ui.vstack(gap="md", classes="p-6"):
        ui.button("reset", on_click=reset_chips, id="reset")
        ui.button("tick", on_click=tick, id="tick")
        reported()
        local()


app.include(__name__)


@pytest.fixture(scope="module")
def base_url():
    with audit_server(app) as url:
        yield url


_SHOWN = """(zone) => [...document.querySelectorAll(
    '[data-bz-zone] [bz-show="open"]')]
    .filter(el => el.closest('[data-bz-zone]').textContent.includes(zone))
    .filter(el => getComputedStyle(el).display !== 'none')
    .map(el => el.textContent.trim())"""


def _shown(page_, zone: str) -> list[str]:
    return page_.evaluate(_SHOWN, zone)


def test_the_next_chip_is_not_hidden_with_the_one_closed(base_url) -> None:
    with browser_page(base_url, "/") as page_:
        page_.wait_for_selector("html.bz-ready", state="attached")
        assert _shown(page_, "Alpha") == ["Alpha", "Bravo", "Charlie"]

        page_.locator("[bz-show=open]", has_text="Alpha").locator("button").click()
        page_.wait_for_function(
            "!document.body.textContent.includes('Alpha')"
        )
        page_.wait_for_timeout(250)
        assert _shown(page_, "Bravo") == ["Bravo", "Charlie"], (
            "la puce qui prend la place de celle qu'on a fermée hérite de son "
            "`open: false` — le rendu du serveur ne re-sème pas `open`."
        )

        page_.click("#reset")
        page_.wait_for_function("document.body.textContent.includes('Alpha')")
        page_.wait_for_timeout(250)
        assert _shown(page_, "Alpha") == ["Alpha", "Bravo", "Charlie"]


def test_a_local_dismiss_survives_a_neighbouring_refresh(base_url) -> None:
    """Le versant licite : sans handler serveur, personne d'autre que le
    navigateur ne sait qu'elle est fermée — un refresh ne la rouvre pas."""
    with browser_page(base_url, "/") as page_:
        page_.wait_for_selector("html.bz-ready", state="attached")
        page_.locator("[bz-show=open]", has_text="Local").locator("button").click()
        page_.wait_for_timeout(150)
        assert _shown(page_, "ticks") == []

        page_.click("#tick")
        page_.wait_for_function(
            "document.querySelector('#ticks').textContent.includes('1')"
        )
        page_.wait_for_timeout(250)
        assert _shown(page_, "ticks") == [], "un refresh a rouvert une fermeture locale"
