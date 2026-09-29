"""Default :class:`BarChart` theme.

Slot inventory :

- ``wrapper``    : outer ``<div>`` hosting the SVG and the legend.
- ``svg``        : the chart SVG itself.
- ``bar``        : bar fill — the ``--bz-solid`` step, set per series
                   (each series gets its own bridge).
- ``axis``       : axis line stroke + the tick line strokes.
- ``axis_label`` : tick text fill + sizing.
- ``gridline``   : faint horizontal helpers behind the bars.
- ``value_label``: optional in-chart number above each bar.
- ``segment_label``: the percentage inside a ``stacked_100`` segment
  (contrasts against the segment fill, unlike ``value_label``).
- ``legend``     : legend row container (HTML, not SVG — text wraps nicely).
- ``legend_dot`` : the colour swatch next to each series name.
- ``legend_label``: legend text fill + sizing.
- ``empty``      : centered "no data" text when the series is empty.

``sizes`` is a dict per step — height + axis font + bar padding ratio.
``palette`` is the auto-cycle for multi-series when no per-series color
is set.
"""

from __future__ import annotations

from typing import Any

BAR_CHART_THEME: dict[str, Any] = {
    "slots": {
        # Fills its container: the plot is drawn in percentages of it
        # (``_svg.PLOT_SPAN``). The svg's width is set by
        # ``_layers.plot_svg`` (container less the axis margins).
        "wrapper":      "flex flex-col gap-3 w-full min-w-0",
        "svg":          "block overflow-visible",
        # ``transition-[y,height,opacity]`` morphs the bar on data
        # refresh (grow / shrink smoothly). ``bz-bar-entry`` runs
        # once on first paint and scales the bar up from its
        # baseline (CSS keyframe in ``render/shell.py``).
        "bar": (
            "fill-(--bz-solid) "
            "transition-[y,height,opacity] duration-400 ease-out "
            "bz-bar-entry"
        ),
        "axis":         "stroke-text/30",
        "axis_label":   "fill-text/60",
        "gridline":     "stroke-text/10",
        # Reference lines — same recipe as LineChart's theme : the
        # reference's bridge carries its colour, so
        # ``Reference(color="success")`` paints a green threshold
        # while a bare ``Reference(value=...)`` falls back to muted.
        "reference_line":  "stroke-(--bz-solid)/60",
        # The label is painted OVER the bars (it passed under them), so
        # it gets a halo in the page colour to stay readable on a fill,
        # and gives the hover back to the bar beneath.
        "reference_label": (
            "fill-(--bz-solid)/80 font-medium pointer-events-none "
            "stroke-background stroke-3 [paint-order:stroke]"
        ),
        "value_label":  "fill-text font-medium",
        # A label placed INSIDE a coloured segment (the stacked_100
        # variant), not above a bar: it must contrast with the fill,
        # hence ``--bz-on-solid`` (the foreground colour of the segment's
        # tint) where ``value_label`` uses the page's text colour.
        # ``pointer-events-none`` so as not to steal the hover from the
        # rect that carries the tooltip.
        "segment_label": (
            "fill-(--bz-on-solid) font-medium pointer-events-none "
            "select-none"
        ),
        "legend":       "flex flex-wrap items-center justify-center gap-x-4 gap-y-1",
        "legend_dot":   "size-3 rounded-selector shrink-0 bg-(--bz-solid)",
        "legend_label": "text-xs text-text/70",
        "empty":        "fill-text/40 text-sm",
    },
    "sizes": {
        # name → {height_px, axis_font_px, bar_padding_ratio, value_font_px}
        "xs": {"h": 140, "axis": 10, "pad": 0.25, "value": 10},
        "sm": {"h": 200, "axis": 11, "pad": 0.20, "value": 10},
        "md": {"h": 280, "axis": 12, "pad": 0.20, "value": 11},
        "lg": {"h": 360, "axis": 13, "pad": 0.18, "value": 12},
        "xl": {"h": 440, "axis": 14, "pad": 0.15, "value": 13},
    },
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
