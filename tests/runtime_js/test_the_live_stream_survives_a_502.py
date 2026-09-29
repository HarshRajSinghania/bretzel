"""Le flux temps réel revient après un 502, et rattrape ce qu'il a manqué.

Le fait gardé
--------------
``EventSource`` retente seul un flux coupé — mais une reprise à laquelle
on répond autre chose qu'un ``200 text/event-stream`` le FERME pour de
bon (``readyState === CLOSED``, c'est le spec). Or c'est exactement ce
que répond un proxy pendant que l'app redémarre : un 502.

Mesuré le 2026-09-26 sur la démo publique, derrière Cloudflare : le
redémarrage planifié du conteneur coupait le flux à 11:00:11, la reprise
recevait un 502, et l'onglet restait sourd au temps réel jusqu'à ce que
quelqu'un recharge — sans rien afficher d'autre qu'une ligne rouge en
console.

Deux choses sont vérifiées ici, sur un client qui écoute pendant qu'un
autre agit :

1. le flux se rouvre une fois le 502 passé (``LiveConnection`` revient) ;
2. ce qui a été diffusé PENDANT la coupure apparaît quand même : le
   broker ne rejoue rien, donc c'est la réouverture qui doit relire les
   zones abonnées.

Le 502 est simulé par ``page.route`` : c'est la réponse d'un proxy, pas
de l'app, donc rien côté serveur ne peut la produire honnêtement.

Lourd (uvicorn + Chromium) — à lancer explicitement ::

    py -m pytest tests/runtime_js/test_the_live_stream_survives_a_502.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, refreshable, ui
from bretzel.state import AppState, field
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser


class Compteur(AppState):
    """Partagé par tous les clients."""

    n: int = field(default=0, merge="add")


def incrementer() -> None:
    Compteur().n += 1


@refreshable(deps=[Compteur], broadcast=[Compteur])
def zone() -> None:
    ui.text(f"n={Compteur().n}", classes="bz-probe-valeur")


@page("/")
def accueil() -> None:
    zone()
    ui.button("plus", on_click=incrementer)


def make_app() -> Bretzel:
    app = Bretzel(title="sse-502", secret_key="sse-502-bench-secret-0123456789",
                  mode="dev")
    app.include(accueil, zone)
    return app


_CONNECTE = "window.$bz && $bz.state.LiveConnection.default.connected === true"

def vaut(n: int) -> str:
    return (
        "() => { const e = document.querySelector('.bz-probe-valeur');"
        f" return !!e && e.textContent.trim() === 'n={n}'; }}"
    )


def test_the_stream_reopens_after_a_502_and_catches_up() -> None:
    bloque = {"actif": True, "refus": 0}

    def proxy(route) -> None:
        if bloque["actif"]:
            bloque["refus"] += 1
            route.fulfill(status=502, body="Bad Gateway")
        else:
            route.continue_()

    with (
        audit_server(make_app()) as base_url,
        browser_page(base_url, "/", wait_until="load") as acteur,
        browser_page(base_url, "/", wait_until="load") as spectateur,
    ):
        spectateur.route("**/_bretzel/sse**", proxy)
        spectateur.reload(wait_until="load")
        spectateur.wait_for_function(vaut(0), timeout=5000)
        spectateur.wait_for_timeout(300)
        assert bloque["refus"] >= 1, "le flux n'a jamais été tenté"

        # Diffusé PENDANT la coupure : le spectateur ne peut pas le recevoir.
        acteur.get_by_role("button", name="plus").click()
        acteur.wait_for_function(vaut(1), timeout=5000)

        bloque["actif"] = False
        spectateur.wait_for_function(_CONNECTE, timeout=15000)
        # Le flux est revenu ; ce qui a été diffusé pendant la coupure doit
        # être relu (le broker ne rejoue rien).
        spectateur.wait_for_function(vaut(1), timeout=5000)
