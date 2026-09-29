"""Le texte du calendrier ne se chevauche à aucun palier, même dense.

Ce que ça ferme, mesuré le 2026-09-29
--------------------------------------
Le calendrier écrit ses BOÎTES en crans de densité (``w-9`` une cellule,
``w-69`` la racine, ``calc(var(--spacing) * n)``) et son TEXTE en paliers
typographiques (``text-xs`` = 11 px), qui ne suivent pas la densité. À
3 px le cran, les en-têtes de colonne débordaient déjà leur cellule à
``xs``, ``sm`` et ``md`` (« LUN.MAR.MER. » collés, de 2 à 11 px), et
l'en-tête « septembre2026 » se collait à ``xs``/``sm``. Sous une densité
serrée (0,15 rem, le plancher du studio de la vitrine), les cinq paliers
débordaient, et la grille des mois (« OctobreNovembre ») aussi.

Même famille que les largeurs de cadre réparées le même jour : une
largeur écrite en crans autour d'un contenu qui n'en est pas.

Ce que le test mesure, et pourquoi dans un navigateur
------------------------------------------------------
Le HTML est IDENTIQUE à 3 px et à 2,4 px le cran : seule la mise en page
décide, donc aucune lecture de classes ne voit le chevauchement. On
mesure l'encre (``Range.getBoundingClientRect`` sur le texte), pas la
boîte : une cellule peut tenir dans sa colonne pendant que son texte en
sort.

Lourd (uvicorn + Chromium) ::

    py -m pytest tests/runtime_js/test_a_dense_calendar_keeps_its_text_apart.py -q -m browser
"""

from __future__ import annotations

import datetime as dt

import pytest

from bretzel import Bretzel, page, ui
from tests.audit.harness import audit_server, browser_page

pytestmark = pytest.mark.browser

SIZES = ("xs", "sm", "md", "lg", "xl")

#: 3 px le cran (le défaut) et 2,4 px (le minimum du studio de la vitrine).
DENSITIES = ("0.1875rem", "0.15rem")

#: Le sous-pixel du moteur de rendu, pas un chevauchement.
SLACK = 0.5


def _app(lang: str) -> Bretzel:
    app = Bretzel(secret_key="d" * 32, title="dense", mode="dev", lang=lang)

    @page("/")
    def home() -> None:
        with ui.vstack(gap="lg", classes="p-6"):
            for size in SIZES:
                with ui.hstack(gap="md", wrap=True, align="start"):
                    # Septembre : le libellé de mois le plus long, dans
                    # les deux langues.
                    with ui.vstack(id=f"jours-{size}"):
                        ui.calendar(value=dt.date(2026, 9, 14), size=size)
                    with ui.vstack(id=f"mois-{size}"):
                        ui.calendar(value="2026-09", mode="month", size=size)

    app.include(home)
    return app


MEASURE = r"""() => {
  const ink = (el) => { const r = document.createRange(); r.selectNodeContents(el);
                        return r.getBoundingClientRect(); };
  const out = {};
  for (const box of document.querySelectorAll('[id^="jours-"],[id^="mois-"]')) {
    const root = box.querySelector('bz-calendar');
    if (!root) continue;
    const faults = [];
    const header = root.querySelector('[data-bz-cal-header]');
    // Les COMMANDES (flèches, déclencheurs), pas les enfants directs :
    // un déclencheur déborde de son enveloppe ``min-w-0`` sans que les
    // enveloppes, elles, se chevauchent.
    const controls = [...header.querySelectorAll('button')]
      .filter(b => !b.closest('[role=menu]'));
    controls.forEach((button, i) => {
      const b = button.getBoundingClientRect(), t = ink(button);
      if (t.width && (t.left < b.left - 0.5 || t.right > b.right + 0.5))
        faults.push('en-tête : l\'encre sort du bouton « ' + button.textContent.trim() + ' »');
      if (i > 0) {
        const gap = b.left - controls[i - 1].getBoundingClientRect().right;
        if (gap < 1) faults.push('en-tête : « ' + controls[i - 1].textContent.trim()
          + ' » et « ' + button.textContent.trim() + ' » collés (' + gap.toFixed(1) + ' px)');
      }
    });
    if (header.scrollWidth > header.clientWidth + 0.5)
      faults.push('en-tête : déborde de ' + (header.scrollWidth - header.clientWidth));
    const rows = [...root.querySelectorAll('[data-bz-cal-weekdays] > div')];
    rows.forEach((cell, i) => {
      const c = cell.getBoundingClientRect(), t = ink(cell);
      if (t.left < c.left - 0.5 || t.right > c.right + 0.5)
        faults.push('jour « ' + cell.textContent + ' » : sort de sa colonne');
      if (i > 0 && t.left - ink(rows[i - 1]).right < 1)
        faults.push('jours « ' + rows[i - 1].textContent + cell.textContent + ' » collés');
    });
    for (const cell of root.querySelectorAll('[data-bz-cal-months] button, [data-bz-cal-grid] button')) {
      const c = cell.getBoundingClientRect(), t = ink(cell);
      if (t.width && (t.left < c.left - 0.5 || t.right > c.right + 0.5))
        faults.push('cellule « ' + cell.textContent.trim() + ' » : le texte sort');
    }
    if (root.scrollWidth > root.clientWidth + 0.5)
      faults.push('racine : déborde de ' + (root.scrollWidth - root.clientWidth));
    out[box.id] = {faults, weekdays: rows.length,
                   cells: root.querySelectorAll('[data-bz-cal-grid] button, [data-bz-cal-months] button').length};
  }
  return out;
}"""


def _density(pg, spacing: str) -> None:
    """Comme le studio de la vitrine : une feuille qui repose ``--spacing``."""
    pg.evaluate(
        """(sp) => {
          let s = document.getElementById('densite');
          if (!s) { s = document.createElement('style'); s.id = 'densite';
                    document.head.appendChild(s); }
          s.textContent = ':root{--spacing:' + sp + '}';
        }""",
        spacing,
    )
    pg.wait_for_timeout(150)


@pytest.fixture(scope="module", params=["fr", "en"])
def mesures(request):
    with audit_server(_app(request.param)) as url, browser_page(url, "/") as pg:
        pg.wait_for_selector("html.bz-ready", state="attached")
        pg.wait_for_timeout(500)
        out = {}
        for spacing in DENSITIES:
            _density(pg, spacing)
            out[spacing] = pg.evaluate(MEASURE)
        yield request.param, out


def test_every_calendar_is_measured(mesures) -> None:
    """Plancher : zéro faute sur zéro calendrier passerait aussi."""
    _, out = mesures
    for spacing, seen in out.items():
        assert len(seen) == 2 * len(SIZES), (spacing, sorted(seen))
        for box, m in seen.items():
            if box.startswith("jours-"):
                assert m["weekdays"] == 7 and m["cells"] == 42, (spacing, box, m)
            else:
                assert m["cells"] == 12, (spacing, box, m)


@pytest.mark.parametrize("spacing", DENSITIES)
def test_no_text_overlaps_at_any_step(mesures, spacing: str) -> None:
    lang, out = mesures
    faults = {box: m["faults"] for box, m in out[spacing].items() if m["faults"]}
    assert not faults, (
        f"[{lang}, --spacing: {spacing}] du texte se chevauche ou sort de sa "
        f"boîte :\n" + "\n".join(f"  {b}: {f}" for b, f in sorted(faults.items()))
        + "\n\nUne boîte écrite en crans suit la densité ; le texte (paliers "
        "text-*) ne la suit pas. La racine doit tenir son contenu "
        "(min-w-max), et le contenu doit tenir dans une colonne."
    )
