"""Un état qu'une zone rafraîchie rencontre pour la première fois est SEMÉ.

Le défaut, trouvé dans l'atelier du cockpit le 2026-09-27
---------------------------------------------------------
Un panneau n'apparaît qu'avec le premier message : c'est une zone
``@refreshable`` rendue par une ACTION, et elle lit un ``ClientState``
que la page n'avait jamais rendu. La réponse d'action ne portait que les
instances SALES — celles que le handler a mutées —, donc rien pour
celle-là. Le runtime lisait ``$bz.state.Panneau.default.ouvert``, le
magasin créait un signal vide pour qu'un effet puisse s'y abonner
(``get`` auto-crée), et trois choses cassaient en silence :

1. le binding valait ``undefined`` — le panneau s'affichait selon un
   défaut que personne n'avait écrit ;
2. la persistance n'était jamais enregistrée (``adoptConfig`` n'est
   appelé que pour une instance semée) : la valeur gardée dans
   ``localStorage`` ne revenait pas ;
3. l'action suivante envoyait le signal vide, que le formulaire écrit
   comme le MOT ``"undefined"``. Un champ ``bool`` le refusait
   (``ValueError: Cannot coerce 'undefined' to bool``), un champ ``str``
   le gardait : une note de version enregistrée « undefined » en base.

La correction, et ses deux versants
-----------------------------------
La réponse d'action SÈME les instances que le navigateur n'a pas
envoyées (``render/partials._render_delta``), avec leur config ; et le
bridge n'envoie plus un champ sans valeur (``05_bridge.js``,
``injectParameters``). Semer ne crée que ce qui manque
(``$bz._store.seed``) : c'est ce qui rend sûr de semer aussi une
instance ``send_to_server=False`` que le navigateur tient déjà — jamais
envoyée, donc toujours « non vue » du serveur. Le troisième test garde ce
versant-là : un correctif qui POUSSERAIT ces instances au lieu de les
semer ferait passer les deux premiers et effacerait, à chaque action,
l'état que le navigateur possède.

Lourd (uvicorn + Chromium) — à lancer explicitement ::

    py -m pytest tests/runtime_js/test_a_state_met_in_a_refreshed_zone_is_seeded.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, refreshable, ui
from bretzel.state import ClientState, PageState, field
from tests.audit.harness import audit_server, browser_page

#: What the server hydrated, action after action — read by the tests.
RECUS: list[tuple[bool, str]] = []


class Panneau(ClientState, persist="local"):
    """Rencontré par la zone seulement, et persisté : les deux moitiés du
    défaut."""

    ouvert: bool = field(default=True)
    note: str = field(default="")


class Occupe(ClientState, send_to_server=False):
    """Posé dans le navigateur, jamais envoyé : le versant qu'un seed ne
    doit pas écraser."""

    actif: bool = field(default=False)


class Fantome(ClientState):
    """Lu par une expression du navigateur que le serveur n'a jamais
    rendue avec l'état : rien ne le sème, son signal reste vide."""

    actif: bool = field(default=False)


#: What the server hydrated for ``Fantome``.
FANTOMES: list[bool] = []


class Vue(PageState):
    montre: bool = field(default=False)
    tour: int = field(default=0)


def montrer() -> None:
    Vue().montre = True


def rafraichir() -> None:
    Vue().tour += 1


def envoyer() -> None:
    panneau = Panneau()
    RECUS.append((panneau.ouvert, panneau.note))


def lire_fantome() -> None:
    FANTOMES.append(Fantome().actif)


@refreshable(deps=[Vue])
def zone() -> None:
    vue = Vue()
    if not vue.montre:
        return
    with ui.vstack(gap="sm", attrs={"data-banc": "panneau"}):
        ui.text(Panneau().note, id="note")
        ui.button("Occuper", id="occuper", on_click=Occupe().actif.set(True),
                  loading=Occupe().actif)
        ui.text(f"tour {vue.tour}", id="tour")


def build_app() -> Bretzel:
    app = Bretzel(secret_key="dev-zone-seed-secret-key", title="zone seed bench",
                  mode="dev")

    @page("/", title="zone")
    def home() -> None:
        # AUCUNE lecture de ``Panneau`` ni d'``Occupe`` ici : c'est ce qui
        # fait que seule la zone, rendue par une action, les rencontre.
        with ui.hstack(gap="sm", classes="p-4"):
            ui.button("Montrer", id="montrer", on_click=montrer)
            ui.button("Rafraîchir", id="rafraichir", on_click=rafraichir)
            ui.button("Envoyer", id="envoyer", on_click=envoyer)
            # A raw read, as a hand-written directive does: the signal is
            # created empty, and no render of ``Fantome`` ever seeds it.
            ui.button("Fantôme", id="fantome", on_click=lire_fantome,
                      attrs={"bz-show": "$bz.state.Fantome.default.actif || true"})
        zone()

    app.include(home)
    return app


@pytest.fixture(scope="module")
def base_url():
    with audit_server(build_app()) as url:
        yield url


def read_store(page, path: str):
    return page.evaluate("(p) => $bz._store.peek(p)", path)


@pytest.mark.browser
def test_the_zone_state_is_seeded_and_sent_back_right(base_url) -> None:
    RECUS.clear()
    with browser_page(base_url, "/") as page:
        assert read_store(page, "Panneau.default.ouvert") is None, (
            "l'instance est connue au départ — le test ne mesurerait pas "
            "ce que la zone rencontre."
        )
        page.click("#montrer")
        page.wait_for_selector("[data-banc=panneau]")
        page.wait_for_timeout(300)
        assert read_store(page, "Panneau.default.ouvert") is True, (
            "la réponse d'action n'a pas semé l'instance que la zone lit : "
            "son binding vaut undefined (``_render_delta``)."
        )

        page.click("#envoyer")
        page.wait_for_timeout(500)
        assert RECUS == [(True, "")], (
            f"le serveur a hydraté {RECUS!r} : un champ sans valeur est "
            "parti comme le mot « undefined »."
        )


@pytest.mark.browser
def test_the_kept_value_comes_back(base_url) -> None:
    """Semer, c'est aussi enregistrer la persistance : la valeur gardée
    dans ``localStorage`` doit gagner sur le défaut du serveur."""
    RECUS.clear()
    with browser_page(base_url, "/") as page:
        page.evaluate("""() => localStorage.setItem('$bz:Panneau.default',
                          JSON.stringify({ouvert: false, note: 'gardée'}))""")
        page.reload()
        page.wait_for_selector("html.bz-ready", state="attached")
        page.click("#montrer")
        page.wait_for_selector("[data-banc=panneau]")
        page.wait_for_timeout(300)
        assert read_store(page, "Panneau.default.note") == "gardée", (
            "la valeur gardée n'est pas revenue : l'instance a reçu ses "
            "champs sans sa config, donc sans persistance."
        )
        page.click("#envoyer")
        page.wait_for_timeout(500)
        assert RECUS == [(False, "gardée")], RECUS


@pytest.mark.browser
def test_a_seed_leaves_what_the_browser_holds(base_url) -> None:
    """Le versant LICITE : une instance jamais envoyée est « non vue » à
    chaque action — elle est donc re-semée, et ne doit rien perdre."""
    with browser_page(base_url, "/") as page:
        page.click("#montrer")
        page.wait_for_selector("[data-banc=panneau]")
        page.wait_for_timeout(300)
        page.click("#occuper")
        page.wait_for_timeout(200)
        assert read_store(page, "Occupe.default.actif") is True, (
            "le clic n'a pas posé la valeur — le reste ne prouverait rien."
        )
        page.click("#rafraichir")
        page.wait_for_selector("#tour:has-text('tour 1')")
        page.wait_for_timeout(300)
        assert read_store(page, "Occupe.default.actif") is True, (
            "la réponse d'action a écrasé une valeur que le navigateur "
            "tenait : elle a POUSSÉ une instance non vue au lieu de la SEMER."
        )


@pytest.mark.browser
def test_an_empty_field_is_not_sent(base_url) -> None:
    """Le bridge, seul : un signal jamais semé n'a rien à dire. Envoyé,
    il deviendrait le MOT « undefined » — refusé par un ``bool``."""
    FANTOMES.clear()
    with browser_page(base_url, "/") as page:
        assert read_store(page, "Fantome.default.actif") is None, (
            "le signal a une valeur — le test ne mesurerait pas l'envoi d'un "
            "champ vide."
        )
        page.click("#fantome")
        page.wait_for_timeout(500)
        assert FANTOMES == [False], (
            f"le serveur a hydraté {FANTOMES!r} : un champ sans valeur est "
            "parti dans le corps de la requête (``injectParameters``)."
        )
