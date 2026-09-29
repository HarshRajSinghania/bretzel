"""Gate : le pouce du switch est centré PAR CONSTRUCTION, à toute densité.

Le centrage tenait par un littéral : ``left-[2px] top-[2px]``, soit le
demi-cran d'écart entre la piste et le pouce QUAND un cran valait 4 px.
Le 2026-09-13 la densité est passée à 3 px ; les tailles ont suivi, pas
l'écart. Mesuré le 2026-09-29 : pouce 0,5 px trop bas, et 1 px de l'arrête
d'arrivée contre 2 px de celle de départ — vu par l'utilisateur à l'œil,
pendant que ``probe_switch`` passait (tolérance ±1,5 px, vertical seul).

La propriété n'est pas un nombre de pixels, c'est une ARITHMÉTIQUE sur les
crans, vraie quelle que soit la valeur de ``--spacing`` :

- piste = pouce + 1 cran de haut, et pouce + course + 1 cran de large ;
- le pouce est posé à un demi-cran (``start-0.5 top-0.5``) ;

donc un demi-cran de marge sur les quatre côtés, dans les deux états.
"""

from __future__ import annotations

import re

from bretzel.components.inputs.switch.theme import SWITCH_THEME

_STEP = r"(\d+(?:\.\d+)?)"


def step_of(prefix: str, classes: str) -> float | None:
    """La valeur en crans de l'utilitaire ``prefix`` (``h``, ``w``,
    ``peer-checked:translate-x``) dans une chaîne de classes."""
    match = re.search(rf"(?:^|\s){re.escape(prefix)}-{_STEP}(?:\s|$)", classes)
    return float(match.group(1)) if match else None


def geometry_faults(theme: dict) -> list[str]:
    faults = []
    thumb_slot = theme["slots"]["thumb"].split()
    if not {"start-0.5", "top-0.5"} <= set(thumb_slot):
        faults.append(f"slot thumb : écart {thumb_slot[:3]} au lieu du demi-cran")
    faults += [f"slot thumb : littéral {t}" for t in thumb_slot if "[" in t]
    for size, slots in theme["sizes"].items():
        track_h, track_w = step_of("h", slots["track"]), step_of("w", slots["track"])
        thumb_h, thumb_w = step_of("h", slots["thumb"]), step_of("w", slots["thumb"])
        travel = step_of("peer-checked:translate-x", slots["thumb"])
        if None in (track_h, track_w, thumb_h, thumb_w, travel):
            faults.append(f"{size} : une dimension n'est pas en crans")
            continue
        if thumb_h != thumb_w:
            faults.append(f"{size} : pouce non carré ({thumb_h}×{thumb_w})")
        if track_h != thumb_h + 1:
            faults.append(f"{size} : piste h-{track_h:g} pour un pouce h-{thumb_h:g}")
        if track_w != thumb_w + travel + 1:
            faults.append(f"{size} : w-{track_w:g} ≠ pouce {thumb_w:g} + course "
                          f"{travel:g} + 1")
    return faults


def test_every_size_is_read() -> None:
    assert len(SWITCH_THEME["sizes"]) >= 5


def test_the_switch_thumb_is_centred_by_construction() -> None:
    faults = geometry_faults(SWITCH_THEME)
    assert not faults, "le pouce du switch n'est plus centré :\n  " + "\n  ".join(faults)


def test_the_detector_still_bites() -> None:
    good = {"slots": {"thumb": "absolute start-0.5 top-0.5"},
            "sizes": {"md": {"track": "h-5 w-9",
                             "thumb": "h-4 w-4 peer-checked:translate-x-4"}}}
    assert not geometry_faults(good)
    bad = {"slots": {"thumb": "absolute left-[2px] top-[2px]"},
           "sizes": {"md": {"track": "h-5 w-10",
                            "thumb": "h-4 w-4 peer-checked:translate-x-4"}}}
    assert len(geometry_faults(bad)) == 4
