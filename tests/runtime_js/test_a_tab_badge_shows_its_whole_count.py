"""La pastille d'un onglet de ``ui.bottom_bar`` montre son compte ENTIER.

La pastille est posée en ``absolute`` au coin de l'icône, donc son bloc
conteneur est l'enveloppe de l'icône — une vingtaine de pixels. Or la
racine de ``ui.badge`` plafonne sa largeur à ``min(16rem, 100%)``, un
pourcentage de CE bloc : « 9+ » y était coupé en « 9.. » (mesuré le
2026-09-29, ``scrollWidth`` 15 contre ``clientWidth`` 13).

Pourquoi un vrai navigateur : c'est une largeur calculée, que le HTML ne
dit pas — les deux classes en conflit s'y lisent aussi bien avant
qu'après.

Lourd (uvicorn + Chromium) ::

    py -m pytest tests/runtime_js/test_a_tab_badge_shows_its_whole_count.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

app = Bretzel(
    secret_key="dev-tab-badge-count-secret-key-xxxxxx",
    title="Bretzel · pastille d'onglet",
    mode="dev",
)

_COUNTS = ("3", "9+", "99+", "new")


@page("/")
def home() -> None:
    with ui.bottom_bar():
        for i, count in enumerate(_COUNTS):
            ui.bottom_bar_item(f"Tab {i}", icon="inbox", badge=count, id=f"tab{i}")
        ui.bottom_bar_item("Own", icon="bell", id="own",
                           badge=ui.badge("99+", color="success", size="xs"))


app.include(__name__)


@pytest.fixture(scope="module")
def base_url():
    with audit_server(app) as url:
        yield url


_CLIPPED = """() => [...document.querySelectorAll('[id^=tab], #own')].map(tab => {
    const chip = tab.querySelector('.absolute');
    const cut = [chip, ...chip.querySelectorAll('*')]
        .some(el => el.scrollWidth > el.clientWidth + 0.5);
    return [tab.id, chip.textContent.trim(), cut];
})"""


def test_no_tab_badge_is_cut(base_url) -> None:
    with browser_page(base_url, "/", viewport=(390, 700)) as page_:
        page_.wait_for_selector("html.bz-ready", state="attached")
        page_.wait_for_timeout(200)
        chips = page_.evaluate(_CLIPPED)
        # Le plancher : toutes les pastilles sont là, avec leur texte.
        assert [text for _, text, _ in chips] == [*_COUNTS, "99+"]
        cut = [(tab, text) for tab, text, clipped in chips if clipped]
        assert not cut, (
            f"pastilles coupées : {cut}. La largeur de la pastille est "
            f"plafonnée par un pourcentage de l'enveloppe de l'icône, son "
            f"bloc conteneur en `absolute`."
        )
