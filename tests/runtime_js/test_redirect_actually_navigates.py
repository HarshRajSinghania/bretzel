"""``redirect()`` fait-il VRAIMENT changer l'URL du navigateur ?

``tests/integration/server/test_redirect_header.py`` prouve que l'en-tête
``HX-Redirect`` arrive sur la réponse HTTP. Ça ne prouve pas la moitié qui
compte : que **htmx la lise et navigue**. Tout le pari de
:func:`bretzel.redirect` tient sur ce fait — « htmx traite cet en-tête
nativement, donc il n'y a aucun code runtime à écrire ». Un fait supposé
qui porte une fonctionnalité entière, c'est exactement ce que le kind
``"redirect"`` du bridge était avant d'être retiré : crédible, écrit
noir sur blanc, et faux.

Deux choses que seul un vrai navigateur peut dire ici :

1. le clic navigue effectivement vers la cible (``location.pathname``) ;
2. le bridge ne mange pas la réponse avant qu'htmx ne voie l'en-tête —
   il s'accroche à ``htmx:responseError``, et un redirect est un 200,
   mais c'est une lecture de code, pas une mesure.

Le serveur héberge une app MINIMALE définie ici plutôt que le
playground : la redirection est une propriété du transport, pas d'un
composant, et une page de playground de plus se paierait sur les 68
autres (elle apparaîtrait dans les balayages inter-pages).

Run : ``py -m pytest tests/runtime_js/test_redirect_actually_navigates.py -q -m browser``
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, layout, page, redirect, ui
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

_TARGET = "/facture-42"


def save_invoice() -> None:
    """Le cas nominal : l'URL n'existe qu'après la mutation."""
    redirect(_TARGET)


_probe_app = Bretzel(secret_key="p" * 32, mode="dev")


@page("/depart")
def depart_page() -> None:
    ui.button("Enregistrer", on_click=save_invoice, id="go")


@page(_TARGET)
def arrivee_page() -> None:
    ui.text("facture 42", id="arrivee")


_probe_app.include(depart_page, arrivee_page)


def save_in_the_shell() -> None:
    redirect("/coque/arrivee")


@layout
def coque() -> None:
    ui.text("menu", id="menu")
    ui.link("Arrivee", href="/coque/arrivee", id="lien")
    ui.outlet()


@page("/coque/depart", layout=coque, title="depart")
def coque_depart() -> None:
    ui.button("Enregistrer", on_click=save_in_the_shell, id="go")


@page("/coque/arrivee", layout=coque, title="arrivee")
def coque_arrivee() -> None:
    ui.text("arrivee dans la coque", id="arrivee")


_probe_app.include(coque_depart, coque_arrivee)


def test_click_on_a_redirecting_action_changes_the_url() -> None:
    with audit_server(_probe_app) as base_url:
        with browser_page(base_url, "/depart") as browser:
            assert browser.evaluate("() => location.pathname") == "/depart"

            browser.click("#go")
            # La navigation est un vrai chargement de document : on attend
            # l'URL, pas un délai fixe (un sleep transformerait une
            # régression en test intermittent).
            browser.wait_for_url(f"**{_TARGET}", timeout=5000)

            assert browser.evaluate("() => location.pathname") == _TARGET
            # …et la page d'arrivée s'est bien rendue, pas juste l'URL.
            assert browser.locator("#arrivee").inner_text() == "facture 42"


def test_inside_a_shared_layout_only_the_outlet_changes() -> None:
    """Comme un lien : la coque reste montée, le document n'est PAS
    rechargé. Le témoin posé sur ``window`` ne survit qu'à ce prix."""
    with (
        audit_server(_probe_app) as base_url,
        browser_page(base_url, "/coque/depart") as browser,
    ):
        browser.evaluate("() => { window.__temoin = 'vivant'; }")

        browser.click("#go")
        browser.wait_for_url("**/coque/arrivee", timeout=5000)
        browser.wait_for_selector("#arrivee", timeout=5000)

        assert browser.locator("#arrivee").inner_text() == "arrivee dans la coque"
        assert browser.evaluate("() => window.__temoin") == "vivant"
        assert browser.locator("#menu").count() == 1
        assert browser.title() == "arrivee"


@pytest.mark.parametrize("trigger", ["#go", "#lien"], ids=["redirect", "link"])
def test_the_tab_title_follows_a_partial_navigation(trigger: str) -> None:
    """Une réponse partielle n'a pas de ``<head>`` : le titre voyage dans
    ``HX-Trigger``. Sans écouteur, l'onglet gardait le titre de la page
    d'avant, après un lien comme après un ``redirect()``."""
    with (
        audit_server(_probe_app) as base_url,
        browser_page(base_url, "/coque/depart") as browser,
    ):
        assert browser.title() == "depart"
        browser.evaluate("() => { window.__temoin = 'vivant'; }")

        browser.click(trigger)
        browser.wait_for_selector("#arrivee", timeout=5000)

        assert browser.evaluate("() => window.__temoin") == "vivant"
        browser.wait_for_function("() => document.title === 'arrivee'", timeout=3000)
