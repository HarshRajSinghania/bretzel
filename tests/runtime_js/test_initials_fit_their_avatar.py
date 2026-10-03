"""Deux initiales tiennent dans le disque d'un avatar, à chaque taille.

``text-xs`` est le plus petit palier de texte : c'est donc le DISQUE qui
doit laisser la place. Depuis la densité à 3 px par cran (2026-09-13),
``h-6`` ne fait plus que 18 px, et deux initiales en graisse moyenne
débordaient du plus petit avatar — « SD » sur les cartes du kanban,
mesuré le 2026-10-01 sur une capture. Aucune vérification ne le voyait :
les classes étaient justes, c'est l'échelle qui avait bougé dessous.

La mesure porte sur « MW », la paire la plus large qu'``initials_of``
puisse rendre en capitales, et sur les DEUX remplissages : la graisse
est la même, mais une variante qui en changerait la ferait diverger.

Lourd (uvicorn + Chromium) — à lancer explicitement ::

    py -m pytest tests/runtime_js/test_initials_fit_their_avatar.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from bretzel.components.feedback.avatar.theme import AVATAR_THEME
from tests.audit.harness import audit_server, browser_page

#: Les paliers mesurés : ceux du thème livré, lus et non recopiés, pour
#: qu'un palier ajouté demain soit mesuré sans qu'on y pense.
TAILLES: tuple[str, ...] = tuple(AVATAR_THEME["sizes"])

app = Bretzel(secret_key="f" * 32, title="Bretzel · initiales", mode="dev")


@page("/")
def home() -> None:
    with ui.vstack(gap="md", classes="p-4"):
        for variante in ("soft", "solid"):
            with ui.hstack(gap="md", align="center"):
                for taille in TAILLES:
                    ui.avatar(initials="MW", size=taille, variant=variante,
                              id=f"{variante}-{taille}")


app.include(__name__)


@pytest.fixture(scope="module")
def base_url():
    with audit_server(app) as url:
        yield url


MESURE = """() => [...document.querySelectorAll('[id^=soft-], [id^=solid-]')]
  .map(n => {
    const disque = n.getBoundingClientRect();
    const lettres = n.querySelector('span').getBoundingClientRect();
    return {id: n.id, disque: disque.width, lettres: lettres.width};
  })"""


@pytest.mark.browser
def test_every_size_is_measured(base_url: str) -> None:
    """Plancher : chaque palier rend un disque et des lettres mesurables.

    Une page qui ne rendrait rien — ou un sélecteur qui ne trouverait
    plus le ``<span>`` des initiales — laisserait la mesure d'à côté
    verte sur une liste vide.
    """
    with browser_page(base_url, "/") as pg:
        pg.wait_for_selector("html.bz-ready")
        mesures = pg.evaluate(MESURE)
    assert len(mesures) == 2 * len(TAILLES) >= 12, mesures
    assert all(m["disque"] > 0 and m["lettres"] > 0 for m in mesures), mesures


@pytest.mark.browser
def test_two_initials_fit_inside_the_disc(base_url: str) -> None:
    with browser_page(base_url, "/") as pg:
        pg.wait_for_selector("html.bz-ready")
        mesures = pg.evaluate(MESURE)
    debordent = [f"{m['id']} : {m['lettres']:.1f} px de lettres dans "
                 f"{m['disque']:.1f} px"
                 for m in mesures if m["lettres"] > m["disque"]]
    assert not debordent, (
        "des initiales débordent de leur avatar :\n  "
        + "\n  ".join(debordent)
        + "\nC'est le disque qui doit grandir : text-xs est déjà le plus "
          "petit palier de texte.")
