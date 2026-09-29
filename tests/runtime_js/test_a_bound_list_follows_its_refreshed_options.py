"""Un select lié à un ``ClientState`` suit ses options après un refresh.

La valeur d'un ``ui.select`` / ``ui.combobox`` lié vit dans le magasin
client ; ses OPTIONS, elles, viennent du serveur. Elles voyagent dans le
``bz-data`` (``_options``, et ``_labels`` pour le select), et ``absorb``
ne réécrit JAMAIS un signal existant : une config que le serveur change
n'arrive dans le scope que si ``_serverSync`` la nomme.

En mode local, les deux composants la nommaient. En mode lié, ils ne
nommaient RIEN — la branche « binding » ne posait aucun marqueur, alors
que la config reste au serveur quel que soit le propriétaire de la
valeur. Slider, NumberInput, Pagination, Stepper et Accordion, eux, la
re-semaient dans les deux modes.

Ce que ça donne à l'écran : l'option ajoutée par le serveur est bien
DESSINÉE (les boutons d'option sont rendus côté serveur, le morph les
apporte), on peut cliquer dessus, la valeur s'écrit dans le magasin — et
le déclencheur n'affiche pas son libellé, parce que ``_labelOf`` lit une
table figée au premier montage.

Pourquoi un vrai navigateur : c'est le morph d'un ``@refreshable`` sur un
aller-retour HTTP qui laisse le scope en place. Monter le composant deux
fois ne reproduit rien (memory
``project_gate_harness_must_match_render_timing``).

Lourd (uvicorn + Chromium) ::

    py -m pytest tests/runtime_js/test_a_bound_list_follows_its_refreshed_options.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, refreshable, ui
from bretzel.state import ClientState, SessionState, field
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

app = Bretzel(
    secret_key="dev-bound-options-refresh-secret-key",
    title="Bretzel · options d'un select lié",
    mode="dev",
)


class Pick(ClientState, persist="memory"):
    fruit: str = field(default="")
    city: str = field(default="")


class Catalog(SessionState):
    grown: bool = field(default=False)


def grow() -> None:
    Catalog().grown = True


def fruits() -> list[tuple[str, str]]:
    return [("a", "Apple"), *([("b", "Banana")] if Catalog().grown else [])]


@refreshable(deps=[Catalog])
def zone() -> None:
    with ui.vstack(gap="sm"):
        ui.text(f"grown = {Catalog().grown}", id="state")
        ui.select(fruits(), value=Pick().fruit, placeholder="choisir", id="sel")
        ui.combobox(fruits(), value=Pick().city, placeholder="chercher", id="cb")


@page("/")
def home() -> None:
    with ui.vstack(gap="md", classes="p-6"):
        ui.button("grow", on_click=grow, id="grow")
        zone()


app.include(__name__)


@pytest.fixture(scope="module")
def base_url():
    with audit_server(app) as url:
        yield url


def _grow(page_) -> None:
    page_.wait_for_selector("html.bz-ready")
    page_.click("#grow")
    page_.wait_for_function(
        "document.querySelector('#state').textContent.includes('True')"
    )
    page_.wait_for_timeout(250)


def test_a_bound_select_labels_an_option_added_by_a_refresh(base_url) -> None:
    with browser_page(base_url, "/") as page_:
        _grow(page_)
        # Le plancher : l'option est bien là. Sans lui, un select qui ne
        # dessinerait plus rien ferait échouer la suite pour une autre
        # raison que celle testée.
        assert page_.locator("#sel [role=option][data-value=b]").count() == 1

        page_.click("#sel button[role=combobox]")
        page_.click("#sel [role=option][data-value=b]")
        page_.wait_for_timeout(150)
        # Le choix a bien ATTERRI dans le magasin : seul l'affichage peut
        # donc être en cause ci-dessous.
        assert page_.evaluate("() => $bz.state.Pick.default.fruit") == "b"

        label = page_.locator("#sel button[role=combobox] span").first.inner_text()
        assert label == "Banana", (
            f"le déclencheur affiche {label!r} après avoir choisi une option "
            f"ajoutée par le serveur. `_labels` est resté figé au premier "
            f"montage : en mode lié, `_serverSync` ne nomme pas la config."
        )


def test_a_bound_combobox_labels_an_option_added_by_a_refresh(base_url) -> None:
    with browser_page(base_url, "/") as page_:
        _grow(page_)
        assert page_.locator("#cb [role=option][data-value=b]").count() == 1

        page_.click("#cb input[type=text]")
        page_.click("#cb [role=option][data-value=b]")
        page_.wait_for_timeout(150)
        assert page_.evaluate("() => $bz.state.Pick.default.city") == "b"

        shown = page_.eval_on_selector("#cb input[type=text]", "el => el.value")
        assert shown == "Banana", (
            f"le champ affiche {shown!r} après avoir choisi une option "
            f"ajoutée par le serveur. `_options` est resté figé au premier "
            f"montage : en mode lié, `_serverSync` ne nomme pas la config."
        )
