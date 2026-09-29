"""Gate : controls on one row share ONE ladder per size — height and text.

A Button next to an Input on the same row must be the same height — and at
``md`` every control already was (``h-10``), which is the tell that
equal-height is the intent. But the action family (button / icon_button /
toggle_group) had drifted to ``lg=h-11 xl=h-12`` while the field family
(input / number_input / select / date pickers) used ``lg=h-12 xl=h-14``, so a
large button sat 4px shy of a large input (bug 1-H, height axis).

The text axis drifted the same way and was guarded by nothing: at ``sm``
the action family wrote ``text-sm`` and the field family ``text-xs``, so a
search field sat at 11 px beside its 13 px button, in the same 24 px box
(measured on the cockpit's atelier, 2026-09-27). And ``combobox`` wrote its
heights in ``rem`` — 28 to 56 px when the ladder is 21 to 42 — invisible
here because the table below listed eight controls by hand and it was not
one of them. Neither was ``toggle_group`` really: its accessor read a slot
with no height and the test SKIPPED, green, on nothing.

Hence the three parts:

- :data:`CONTROLS` names each control and the slot carrying its height and
  its text; a declared slot that reads nothing FAILS instead of skipping;
- the discovery test finds every component whose size table puts a slot at
  ``h-10`` on ``md`` across the five steps, and refuses one that is
  neither in :data:`CONTROLS` nor in :data:`NOT_CONTROLS` — the next
  control cannot stay out by not being named;
- the mutation test proves the readers still bite, both ways.
"""

from __future__ import annotations

import functools
import re
from collections.abc import Callable, Mapping
from typing import Any

import pytest

from bretzel.components.base import SIZE_SCALE, is_size_keyed
from bretzel.theme import TEXT_SLOT_NAMES
from tests.consistency._discovery import (
    public_component_classes,
    scaled_slots,
    ui_name_of,
)

#: The height a control has at each step — the field family's ladder.
HEIGHT_LADDER = {"xs": "h-7", "sm": "h-8", "md": "h-10", "lg": "h-12", "xl": "h-14"}

#: The size of a control's text at each step. ``md`` stays at ``text-sm``:
#: a control's label sits one step under running text (``text-base``), the
#: way Linear or Ant Design size a 30-32 px control.
TEXT_LADDER = {"xs": "text-xs", "sm": "text-sm", "md": "text-sm",
               "lg": "text-base", "xl": "text-lg"}

#: ``ui`` name → (slot carrying the height, slot carrying the text). ``None``
#: says the axis does not apply, and the comment says why.
CONTROLS: dict[str, tuple[str | None, str | None]] = {
    "button": ("root", "root"),
    # Its ``text-*`` sizes the GLYPH (``iconify-icon`` is 1em), not a label.
    "icon_button": ("root", None),
    "input": ("input", "input"),
    "number_input": ("shell", "input"),
    "select": ("trigger", "trigger"),
    # ``min-h``: the trigger grows with its pills, one line is the ladder.
    "combobox": ("trigger", "trigger"),
    "toggle_group": ("root", "item"),
    "date_picker": ("input_frame", "input_field"),
    "date_range_picker": ("input_frame", "input_field"),
    "month_picker": ("input_frame", "input_field"),
    "week_picker": ("input_frame", "input_field"),
    "time_picker": ("input_frame", "input_field"),
    "color_picker": ("input_frame", "input_field"),
    "pagination": ("item", "item"),
    # ``variant="button"``: the trigger is a button among the controls.
    "file_upload": ("button_padding", "button_padding"),
    # A round arrow over a slide: a glyph, no label.
    "carousel": ("arrow", None),
    # Its height is its number of rows; its text is a field's.
    "textarea": (None, "root"),
    # A pill has no fixed height; its label sits among the controls.
    "tabs": (None, "pill"),
}

#: Components whose size table does land on ``h-10`` at ``md``, and that
#: are not controls on a row. Each says why.
NOT_CONTROLS: dict[str, str] = {
    "avatar": "a portrait: its scale goes to 2xl and ends at h-16, "
              "it sits beside a name, not in a toolbar",
}

# ⚠️ ``(?<![\w-])`` et pas ``\b`` : apres un tiret, ``\b`` est vrai,
# donc ``\bh-(\d+)`` matche AUSSI dans ``max-h-40`` — le lecteur aurait
# rendu « hauteur 40 » pour une hauteur MAXIMALE. Aucun slot de controle
# n'en porte aujourd'hui (mesure le 2026-08-19), donc c'etait un faux
# positif LATENT : c'est le test de mutation ci-dessous qui l'a trouve,
# en verifiant que la regex epargne les formes legitimes. ``min-h-`` est
# lu, lui : c'est la hauteur d'une ligne d'un controle qui grandit.
_H = re.compile(r"(?<![\w-])(min-)?h-(\d+)\b")
#: The text steps, read on the theme's own vocabulary rather than one more
#: hand-written ``xs|sm|base…`` alternation.
_T = re.compile(
    r"(?<![\w-])text-("
    + "|".join(sorted(TEXT_SLOT_NAMES, key=len, reverse=True))
    + r")(?![\w-])"
)


def height_of(classes: str | None) -> str | None:
    m = _H.search(classes or "")
    return f"h-{m.group(2)}" if m else None


def text_of(classes: str | None) -> str | None:
    m = _T.search(classes or "")
    return f"text-{m.group(1)}" if m else None


def slot_at(theme: Mapping[str, Any], slot: str, step: str) -> str | None:
    """The class string ``slot`` takes at ``step``, whatever the nesting.

    Two shapes coexist (cf. ``bretzel.components.base.sizes``): keyed by
    size (``{"sm": "…"}`` for the root, ``{"sm": {"trigger": "…"}}``), or
    by slot (``{"input_frame": {"sm": "…"}}``).
    """
    sizes = theme.get("sizes") or {}
    if is_size_keyed(sizes):
        row = sizes.get(step)
        value = row if isinstance(row, str) and slot == "root" else (
            row.get(slot) if isinstance(row, Mapping) else None
        )
    else:
        value = (sizes.get(slot) or {}).get(step)
    return value if isinstance(value, str) else None


@functools.cache
def themes() -> dict[str, Mapping[str, Any]]:
    return {ui_name_of(cls): cls.THEME for cls in public_component_classes()
            if getattr(cls, "THEME", None)}


def test_every_named_control_exists() -> None:
    """Le plancher : chaque nom de la table désigne un composant livré."""
    known = themes()
    missing = sorted(set(CONTROLS) - set(known))
    assert not missing, f"{missing} : plus de composant de ce nom — la table a pourri"
    assert len(CONTROLS) >= 18


#: The two axes: (index in ``CONTROLS``, reader, ladder).
AXES: dict[str, tuple[int, Callable[[str | None], str | None], dict[str, str]]] = {
    "height": (0, height_of, HEIGHT_LADDER),
    "text": (1, text_of, TEXT_LADDER),
}


@pytest.mark.parametrize("step", SIZE_SCALE)
@pytest.mark.parametrize(
    ("axis", "component"),
    [(axis, name) for axis, (index, _, _) in AXES.items()
     for name, slots in sorted(CONTROLS.items()) if slots[index]],
)
def test_control_matches_ladder(axis: str, component: str, step: str) -> None:
    index, read, ladder = AXES[axis]
    slot = CONTROLS[component][index]
    got = read(slot_at(themes()[component], slot, step))
    assert got == ladder[step], (
        f"{component} size='{step}' : le slot {slot!r} rend {got}, attendu "
        f"{ladder[step]} — à palier égal, les contrôles d'une rangée "
        f"partagent leur {axis} ({ladder}). ``None`` veut dire que le slot "
        f"déclaré ne la porte plus : corrige la table, ne la saute pas."
    )


def ladder_candidates(theme: Mapping[str, Any]) -> list[str]:
    """The slots that sit at ``h-10`` on ``md`` and have a height at every
    step — the shape of a control, whatever its name."""
    return sorted(
        slot for slot in scaled_slots(theme.get("sizes") or {})
        if height_of(slot_at(theme, slot, "md")) == "h-10"
        and all(height_of(slot_at(theme, slot, s)) for s in SIZE_SCALE)
    )


def test_no_control_escapes_the_ladder() -> None:
    """La découverte : un contrôle ne sort pas de la gate en n'étant pas nommé."""
    found = {name for name, theme in themes().items() if ladder_candidates(theme)}
    assert len(found) >= 15, f"seulement {sorted(found)} — le lecteur ne voit plus rien"
    stray = sorted(found - set(CONTROLS) - set(NOT_CONTROLS))
    assert not stray, (
        f"{stray} : un slot à h-10 sur md, sur les cinq paliers — c'est la "
        f"forme d'un contrôle. Ajoute-le à CONTROLS (et aligne-le), ou à "
        f"NOT_CONTROLS avec sa raison."
    )
    stale = sorted(set(NOT_CONTROLS) - found)
    assert not stale, f"{stale} : n'a plus la forme d'un contrôle, retire l'exemption"


def test_the_detector_still_bites() -> None:
    """Mutation : la hauteur et le texte d'un contrôle sont encore lus.

    Si ``_H`` ou ``_T`` cessait de matcher, les deux lecteurs rendraient
    ``None`` partout et la comparaison porterait sur du vide — un bouton
    4 px plus court qu'un champ passerait, comme avant la gate.
    """
    assert height_of("inline-flex h-10 px-4") == "h-10"
    assert height_of("min-h-8 px-3 py-1") == "h-8"
    assert text_of("h-8 px-3 text-sm") == "text-sm"
    assert text_of("px-5 text-2xl") == "text-2xl"
    for licit in ("max-h-10", "h-full", "h-[2.5rem]", "min-h-[2rem]"):
        assert height_of(licit) is None, f"{licit!r} : faux positif"
    for licit in ("text-muted", "text-center", "text-(--bz-text)", "context-sm"):
        assert text_of(licit) is None, f"{licit!r} : faux positif"
    # A fabricated drift is seen by the comparison itself.
    drifted = {"sizes": {"sm": {"input": "h-9 px-3 text-xs"}}}
    assert height_of(slot_at(drifted, "input", "sm")) != HEIGHT_LADDER["sm"]
    assert text_of(slot_at(drifted, "input", "sm")) != TEXT_LADDER["sm"]
