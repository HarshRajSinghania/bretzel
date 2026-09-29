"""Le balayage ne prend pas un ``sr-only`` pour du contenu coupé.

Le faux positif, trouvé en posant ``ui.file_upload(variant="button")``
dans l'atelier du cockpit le 2026-09-27 : son ``<input type="file">``
natif est ``sr-only`` — 1 px, ``overflow:hidden`` — parce que le
composant le pilote et que personne ne doit le voir. Le constat « nothing
is clipped without recourse » le lisait comme une boîte de 1 px qui en
demandait 19, et rougissait chaque page portant le composant.

Les deux versants, sur une vraie page : la boîte masquée exprès se tait,
et une boîte RÉELLEMENT coupée — trois lignes dans la hauteur d'une —
rougit toujours. Sans le second, exclure tout ``overflow:hidden``
passerait ce test et rendrait le constat muet.

``tests/unit/probe/test_the_sweep_sees_clipped_content.py`` exerce la
DÉCISION sur une sortie fabriquée ; la collecte, elle, est du JavaScript,
et ne se mesure que dans un navigateur.

Lourd (uvicorn + Chromium) — à lancer explicitement ::

    py -m pytest tests/runtime_js/test_the_sweep_leaves_a_visually_hidden_box_alone.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from bretzel.probe._sweep import _GEOMETRY_JS
from tests.audit.harness import audit_server, browser_page


def build_app() -> Bretzel:
    app = Bretzel(secret_key="dev-sweep-sr-only-secret-key", title="sweep bench",
                  mode="dev")

    @page("/", title="sweep")
    def home() -> None:
        with ui.vstack(gap="md", classes="p-6"):
            ui.file_upload(variant="button", list="chips", name="pieces")
            with ui.vstack(gap="none", classes="h-6 overflow-hidden w-64",
                           attrs={"data-banc": "coupee"}):
                for line in ("première ligne", "deuxième ligne", "troisième ligne"):
                    ui.text(line)

    app.include(home)
    return app


@pytest.fixture(scope="module")
def base_url():
    with audit_server(build_app()) as url:
        yield url


@pytest.mark.browser
def test_a_visually_hidden_input_is_not_clipped_content(base_url) -> None:
    with browser_page(base_url, "/") as page:
        assert page.locator("input[type=file].sr-only").count() == 1, (
            "le composant n'émet plus son input sr-only — le test ne "
            "mesurerait plus le faux positif."
        )
        clipped = page.evaluate(_GEOMETRY_JS)["clipped"]
        assert not [c for c in clipped if c["tag"] == "input"], (
            f"le balayage signale encore l'input masqué exprès : {clipped}"
        )
        assert [c for c in clipped if "première ligne" in c["text"]], (
            f"la boîte réellement coupée n'est plus signalée : {clipped} — "
            "l'exclusion est trop large."
        )
