"""``ui.file_upload(variant="button")`` a la largeur d'un bouton.

Ce que ça ferme, mesuré le 2026-09-29
--------------------------------------
La racine partagée par les deux variantes portait ``w-full`` et une
colonne flex étirée : le déclencheur compact prenait donc toute la
largeur de son conteneur — une barre bordée de 600 px pour un libellé
« Attach » — et, dans un ``hstack``, poussait son voisin au bout de la
ligne. La vitrine le contournait avec ``classes="items-start"``.

La ``dropzone``, elle, remplit sa ligne : c'est une surface de dépôt,
et le versant licite est mesuré ici aussi.

Lourd (uvicorn + Chromium) ::

    py -m pytest tests/runtime_js/test_a_file_upload_button_hugs_its_label.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

app = Bretzel(secret_key="f" * 32, title="upload", mode="dev")


@page("/")
def home() -> None:
    with ui.vstack(gap="lg", classes="p-6 w-[40rem]"):
        with ui.hstack(gap="sm", id="rangee"):
            ui.file_upload(variant="button", label="Attach", id="bouton")
            ui.button("Voisin", id="voisin")
        with ui.vstack(id="pile"):
            ui.file_upload(variant="button", label="Attach", id="bouton-pile")
        with ui.hstack(gap="sm", id="rangee-zone"):
            ui.file_upload(label="Drop here", id="zone")


app.include(__name__)

MEASURE = r"""() => {
  const w = (sel) => document.querySelector(sel).getBoundingClientRect();
  const trigger = (id) => w('#' + id + ' [role=button]');
  return {
    row: w('#rangee').width,
    button: trigger('bouton').width,
    label: (() => { const r = document.createRange();
      r.selectNodeContents(document.querySelector('#bouton [role=button] span'));
      return r.getBoundingClientRect().width; })(),
    neighbourGap: w('#voisin').left - trigger('bouton').right,
    stackButton: trigger('bouton-pile').width,
    stack: w('#pile').width,
    zone: w('#zone').width,
    zoneRow: w('#rangee-zone').width,
  };
}"""


@pytest.fixture(scope="module")
def mesure():
    with audit_server(app) as url, browser_page(url, "/") as pg:
        pg.wait_for_selector("html.bz-ready", state="attached")
        pg.wait_for_timeout(300)
        yield pg.evaluate(MEASURE)


def test_the_page_is_measured(mesure) -> None:
    """Plancher : une rangée vide rendrait « le bouton est étroit » vrai."""
    assert mesure["row"] > 400 and mesure["label"] > 10, mesure


def test_the_button_sizes_to_its_label_in_a_row(mesure) -> None:
    assert mesure["button"] < mesure["label"] + 120, (
        f"le déclencheur mesure {mesure['button']:.0f} px pour un libellé de "
        f"{mesure['label']:.0f} px : il s'étire au lieu d'épouser son contenu."
    )
    assert mesure["neighbourGap"] < 40, (
        f"le voisin est à {mesure['neighbourGap']:.0f} px du bouton : la racine "
        f"prend toute la ligne et le repousse au bout."
    )


def test_the_button_sizes_to_its_label_in_a_stack(mesure) -> None:
    assert mesure["stackButton"] < mesure["stack"] / 2, (
        f"dans une pile de {mesure['stack']:.0f} px, le déclencheur mesure "
        f"{mesure['stackButton']:.0f} px : il s'étire à la largeur de la colonne."
    )


def test_the_dropzone_still_fills_its_row(mesure) -> None:
    """Le versant licite : la surface de dépôt remplit sa ligne."""
    assert mesure["zone"] > mesure["zoneRow"] - 2, (
        f"la dropzone mesure {mesure['zone']:.0f} px dans une ligne de "
        f"{mesure['zoneRow']:.0f} px : elle ne remplit plus sa ligne."
    )
