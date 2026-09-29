"""Default :class:`LineChart` theme.

Slot inventory :

- ``wrapper``    : outer ``<div>``, the width of the chart (the
  container's, or ``width=``'s).
- ``svg``        : the chart SVG — the plot rectangle, its margins are
  CSS (cf. ``_layers.plot_svg``).
- ``line``       : the polyline stroke per series.
- ``area``       : optional area fill under the line.
- ``dot``        : optional per-point marker (when ``show_dots=True``).
- ``dot_active`` : the "you are here" dot rendered per series at the
  cursor's nearest x ; visible only while hovering. Ringed in the page
  colour so it pops off the curve.
- ``crosshair``  : faint dashed vertical rule at the active column,
  connecting the active dots into a readable slice.
- ``hit``        : transparent ``<rect>`` overlays — one per data
  index, drive the hover scope (full-column snap-to-nearest-x, single
  and multi alike).

The value tooltip is the shared floating panel from the ``10_charts.js``
runtime slab (follows the active column, anchored above the plot) — it
is *not* a theme slot, so single and multi read identically.

- ``axis``       : axis line stroke + per-tick line strokes.
- ``axis_label`` : tick text fill + sizing.
- ``gridline``   : faint horizontal helpers behind the data.
- ``legend``     : legend row container.
- ``legend_dot`` : the colour swatch.
- ``legend_label``: legend text fill + sizing.
- ``empty``      : centered "no data" text.

``sizes`` per palier carries ``(h, stroke_w, dot_r, axis_font)``.
``palette`` is the auto-cycle for multi-series.
"""

from __future__ import annotations

from typing import Any

LINE_CHART_THEME: dict[str, Any] = {
    "slots": {
        # ``w-full``: the chart takes its container's width — the plot
        # is drawn in percentages of it (``_svg.PLOT_SPAN``), so the
        # legend, centred on the wrapper, is centred on the chart.
        # ``min-w-0`` lets two charts share a row. It was
        # ``w-fit max-w-full`` while the SVG had a fixed intrinsic width
        # (600): a wide card kept the chart at 600 px on its left.
        "wrapper":      "relative flex flex-col gap-3 w-full min-w-0",
        "svg":          "block overflow-visible",
        # ``transition-[d]`` morphs the path when @refreshable
        # swaps new data. ``bz-area-entry`` reveals the line left to
        # right on first paint, by clipping — the same keyframe as the
        # area, so the two finish together. It was a dash reveal
        # (``bz-line-entry``, ``pathLength="1"``), which the stretched
        # frame breaks: cf. ``line_chart._stretched_frame``.
        # ``drop-shadow-sm`` lifts the line off the gridlines —
        # calibrated to disappear under dark themes.
        "line": (
            "stroke-(--bz-solid) fill-none "
            "transition-[d] duration-500 ease-out "
            "drop-shadow-sm "
            "bz-area-entry"
        ),
        # ``transition-[d]`` morphs the silhouette on data refresh.
        # ``bz-area-entry`` (CSS keyframe in ``render/shell.py``)
        # clip-path reveals the area from left to right in sync with
        # the line's ``bz-line-entry`` draw — both 1100ms so they
        # finish together. Same eternal pattern : fill comes from
        # ``url(#...)`` ; the gradient's colour lives on the
        # ``<linearGradient>`` via ``area_gradient_color``.
        "area": (
            "transition-[d] duration-500 ease-out "
            "bz-area-entry"
        ),
        # Sets ``color`` on the ``<linearGradient>`` so the stops'
        # ``stop-color: currentColor`` resolves to the chart series'
        # palette colour. ``--bz-solid`` comes from the series' bridge
        # — works with any colour name the user's palette declares.
        "area_gradient_color": "text-(--bz-text)",
        "dot":          "fill-(--bz-solid)",
        # "You are here" dot at the active column (one per series).
        # ``stroke-background stroke-2`` rings it in the page colour so
        # it pops off the curve it sits on — the fix for "I cannot
        # see the points". ``transition-[cx,cy]`` glides it along as the
        # cursor sweeps columns.
        "dot_active": (
            "fill-(--bz-solid) stroke-background stroke-2 "
            "transition-[cx,cy] duration-150 ease-out"
        ),
        # Vertical crosshair at the active column. Faint + dashed so it
        # guides the eye without competing with the data ; connects the
        # active dots into a readable slice.
        "crosshair":    "stroke-text/20",
        "hit":          "fill-transparent",
        "axis":         "stroke-text/30",
        "axis_label":   "fill-text/60",
        "gridline":     "stroke-text/10",
        # Reference lines (thresholds / goal markers). ``stroke-`` and
        # ``fill-`` substitute with the ref's colour so a goal can pop
        # in ``success`` green while a baseline sits in muted grey.
        "reference_line":  "stroke-(--bz-solid)/60",
        # Painted OVER the data: a halo in the page colour keeps it
        # readable on a curve or an area, and it gives the hover back to
        # what lies beneath.
        "reference_label": (
            "fill-(--bz-solid)/80 font-medium pointer-events-none "
            "stroke-background stroke-3 [paint-order:stroke]"
        ),
        "legend":       "flex flex-wrap items-center justify-center gap-x-4 gap-y-1",
        # Each legend entry is a ``<button>`` (click to toggle the
        # series). ``cursor-pointer`` + the focus ring let the keyboard
        # path work too. ``transition-opacity`` powers the dim-when-
        # hidden visual the wrapper drives via ``:class``.
        "legend_item":  (
            "flex items-center gap-2 cursor-pointer "
            "transition-opacity duration-150 "
            "outline-none focus-visible:ring-2 focus-visible:ring-text/30 "
            "rounded px-1"
        ),
        # ``bg-(--bz-solid)`` is the killer-feature — without it the
        # swatch is an invisible div and the user has no way to map
        # legend entries to curve colours. Substituted per-series at
        # render time so each entry gets its own palette colour.
        "legend_dot":   "size-3 rounded-selector shrink-0 bg-(--bz-solid)",
        "legend_label": "text-xs text-text/70",
        "empty":        "fill-text/40 text-sm",
    },
    "sizes": {
        # name → {height, stroke_width, dot_radius, axis_font}
        "xs": {"h": 140, "stroke": 1.0,  "dot": 2.0, "axis": 10},
        "sm": {"h": 200, "stroke": 1.25, "dot": 2.5, "axis": 11},
        "md": {"h": 280, "stroke": 1.5,  "dot": 3.0, "axis": 12},
        "lg": {"h": 360, "stroke": 1.75, "dot": 3.5, "axis": 13},
        "xl": {"h": 440, "stroke": 2.0,  "dot": 4.0, "axis": 14},
    },
    # Gradient stop opacities for the area fill — top (under the line)
    # and bottom (at the baseline). Bottom is intentionally non-zero
    # so the area stays the chart's colour throughout instead of
    # fading to the page background (which reads as "dark" on a dark
    # theme). Tweak here to change the fade depth.
    "area_gradient": {"top": 0.45, "bottom": 0.10},
    # The auto-cycle when a series carries no ``color=``. BRAND colours
    # first, then status colours, ``error`` last. The identity's author
    # chose ``primary`` and ``secondary`` as a pair, so they are the two
    # the framework can trust to differ; a status colour is only
    # guaranteed to differ from the OTHER status colours
    # (``test_palette_distinctness``), not from an arbitrary primary. The
    # old cycle went primary → success, so under a green identity the
    # first two series came out the same green. ``info`` next, the only
    # status colour that says nothing; ``error`` last, since a series in
    # red reads as an alarm.
    "palette": (
        "primary", "secondary", "info", "success", "warning", "error",
        "muted",
    ),
}
