"""Probe — les contrôles d'une même rangée tombent sur les mêmes pixels.

Pilote la page ``/ladder`` du playground : une rangée par palier, avec
tous les contrôles qui se posent sur une ligne, puis le texte que personne
ne dimensionne.

Pourquoi un probe en plus de la gate
------------------------------------
``tests/consistency/test_control_height_ladder.py`` lit les TABLES : il
dit que chaque contrôle écrit ``h-8 text-sm`` au palier ``sm``. Il ne dit
pas qu'un wrapper n'ajoute pas un pixel de bordure, qu'une classe compile,
ni ce qu'hérite un texte qui n'écrit AUCUNE classe — et c'était le défaut
principal mesuré sur l'atelier du cockpit le 2026-09-27 : un ``ui.text``
sans ``size=`` prenait les 16 px du navigateur, au-dessus du 14 de
l'échelle, donc un message plus gros que le titre au-dessus de lui.

Constats
--------
① à chaque palier, un contrôle a la hauteur de l'échelle
  (``--spacing`` × 7/8/10/12/14) ;
② à chaque palier, tout texte d'un contrôle a la taille de l'échelle
  (``--text-xs/sm/sm/base/lg``) — textarea et onglets compris ;
③ un texte et un lien sans taille héritent de ``--text-base`` ;
④ aucun texte visible de la page n'est hors des paliers du thème.

Run :  py tests/probes/probe_ladder.py
"""

from __future__ import annotations

import sys

from bretzel.components.base import SIZE_SCALE
from bretzel.probe import Probe, Window, probe
from bretzel.theme import TEXT_SLOT_NAMES
from tests.consistency.test_control_height_ladder import (
    CONTROLS,
    HEIGHT_LADDER,
    TEXT_LADDER,
)
from tests.probes._serve import use_local_tailwind

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

APP = "examples.playground.main:app"

#: What the page shows, read in one pass. A text is an element owning a
#: non-blank text node, or a field (its typed text is not a text node).
#: Hidden things (a closed panel, a teleported popover) have no box and
#: are skipped: they are not on screen. The steps are the theme's own
#: (``TEXT_SLOT_NAMES``), passed in rather than copied.
MEASURE = """(steps) => {
  const root = getComputedStyle(document.documentElement);
  const toPx = v => parseFloat(v) * (v.includes('rem') ? 16 : 1);
  const spacing = toPx(root.getPropertyValue('--spacing'));
  const scale = Object.fromEntries(
    steps.map(s => [s, toPx(root.getPropertyValue('--text-' + s))]));
  const ownsText = e => !e.closest('iconify-icon')
    && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const shown = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const size = e => parseFloat(getComputedStyle(e).fontSize);
  const FIELD = 'input:not([type=hidden]):not([type=checkbox]):not([type=radio])'
              + ':not([type=color]):not([type=range]), textarea';
  const texts = el => [...new Set([el, ...el.querySelectorAll('*')]
    .filter(e => (ownsText(e) || e.matches(FIELD)) && shown(e)).map(size))];
  const controls = [...document.querySelectorAll('[data-ladder]')].map(el => ({
    name: el.dataset.ladder,
    step: el.dataset.ladderStep || el.closest('[data-ladder-row]')?.dataset.ladderRow,
    height: Math.round(el.getBoundingClientRect().height * 10) / 10,
    texts: texts(el),
  }));
  const offScale = [...document.querySelectorAll('body *')]
    .filter(e => ownsText(e) && shown(e))
    .map(e => [e.textContent.trim().slice(0, 30), size(e)])
    .filter(([, px]) => !Object.values(scale).some(v => Math.abs(v - px) < 0.1));
  return {spacing, scale, controls, offScale};
}"""


def measured(name: str, axis: int) -> bool:
    """Does ``name`` carry this axis (0 height, 1 text)? The gate's
    ``CONTROLS`` says it with ``None``; the running text (``text``,
    ``link``) only lives in the ``base`` row."""
    slots = CONTROLS.get(name)
    return slots is None or slots[axis] is not None


def ladder_rows(p: Probe, a: Window) -> None:
    a.goto("/ladder")
    a.settle()
    m = a.page.evaluate(MEASURE, list(TEXT_SLOT_NAMES))
    spacing, scale = m["spacing"], m["scale"]
    by_step: dict[str, list[dict]] = {}
    for c in m["controls"]:
        by_step.setdefault(c["step"], []).append(c)

    p.check("la page porte ses cinq rangées et son texte courant",
            all(s in by_step for s in (*SIZE_SCALE, "base")), sorted(by_step))

    for step in SIZE_SCALE:
        controls = by_step.get(step, [])
        want_h = spacing * int(HEIGHT_LADDER[step].removeprefix("h-"))
        want_t = scale[TEXT_LADDER[step].removeprefix("text-")]
        wrong_h = [(c["name"], c["height"]) for c in controls
                   if measured(c["name"], 0) and abs(c["height"] - want_h) > 0.5]
        p.check(f"① {step} — chaque contrôle fait {want_h:g} px de haut",
                not wrong_h, wrong_h)
        wrong_t = [(c["name"], c["texts"]) for c in controls
                   if measured(c["name"], 1)
                   and (not c["texts"] or any(abs(t - want_t) > 0.1 for t in c["texts"]))]
        p.check(f"② {step} — chaque texte de contrôle fait {want_t:g} px",
                not wrong_t, wrong_t)

    base = scale["base"]
    wrong = [(c["name"], c["texts"]) for c in by_step.get("base", [])
             if any(abs(t - base) > 0.1 for t in c["texts"])]
    p.check(f"③ un texte sans taille hérite de --text-base ({base:g} px)",
            not wrong, wrong)

    p.check("④ aucun texte visible hors des paliers du thème",
            not m["offScale"], m["offScale"][:10])
    a.shot("ladder")


def main() -> None:
    use_local_tailwind()
    with probe(APP, size=(1440, 900)) as p:
        (a,) = p.windows
        ladder_rows(p, a)


if __name__ == "__main__":
    main()
