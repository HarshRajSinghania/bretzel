"""``/sparkline`` — a trend the size of a word."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A trend the size of a word: next to a figure, in a table cell, "
           "in a status list. No axis, no legend, just the shape.")


def kpi(label: str, value: str, delta: str, trend: list[float],
        color: str) -> None:
    with ui.card(padding="md"), ui.vstack(gap="xs"):
        ui.text(label, size="sm", color="muted")
        with ui.hstack(gap="sm", justify="between", align="end"):
            ui.heading(value, level=3, size="2xl")
            ui.sparkline(data=trend, color=color, area_fill=True)
        ui.badge(delta, color=color, variant="soft", size="sm")


def kpi_row() -> None:
    with ui.grid(min_col="12rem", gap="md"):
        kpi("Active users", "12,480", "+8.2% this week",
            [9.1, 9.4, 9.2, 10.1, 10.8, 11.2, 11.9, 12.5], "primary")
        kpi("Conversion", "4.6%", "+0.4 pt",
            [3.9, 4.1, 4.0, 4.3, 4.2, 4.5, 4.4, 4.6], "success")
        kpi("Churn", "2.1%", "+0.3 pt",
            [1.6, 1.7, 1.7, 1.9, 1.8, 2.0, 2.1, 2.1], "error")
        kpi("Avg. response", "72 min", "−9 min",
            [96, 90, 88, 84, 86, 79, 75, 72], "info")


PRODUCTS = [
    {"sku": "BRZ-104", "name": "Linen tote bag", "sold": 1284,
     "trend": [42, 45, 51, 48, 56, 62, 60, 71, 76, 74, 82, 88]},
    {"sku": "BRZ-221", "name": "Ceramic pour-over", "sold": 962,
     "trend": [70, 68, 72, 66, 64, 67, 61, 63, 58, 60, 57, 55]},
    {"sku": "BRZ-087", "name": "Wool throw, charcoal", "sold": 740,
     "trend": [20, 22, 21, 30, 44, 41, 52, 58, 55, 63, 70, 68]},
    {"sku": "BRZ-310", "name": "Oak serving board", "sold": 518,
     "trend": [38, 41, 37, 40, 39, 42, 40, 43, 41, 44, 42, 43]},
]


def trend_cell(value, row):
    rising = value[-1] >= value[0]
    return ui.sparkline(data=value, color="success" if rising else "error",
                        size="sm", show_last_dot=True)


def product_table() -> None:
    ui.table(rows=PRODUCTS, row_key="sku", columns=[
        ui.column("sku", label="SKU"),
        ui.column("name", label="Product"),
        ui.column("sold", label="Units sold", align="right"),
        ui.column("trend", label="Last 12 weeks", render=trend_cell),
    ])


def service(name: str, uptime: str, latency: list[float], color: str,
            icon: str) -> None:
    with ui.hstack(gap="md", justify="between", align="center"):
        with ui.hstack(gap="sm", align="center"):
            ui.icon(icon, size="sm", color=color)
            ui.text(name, weight="medium")
        with ui.hstack(gap="md", align="center"):
            ui.sparkline(data=latency, color=color, smooth=False, size="sm")
            ui.text(uptime, size="sm", color="muted")


def status_list() -> None:
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="sm"):
        ui.heading("System status", level=3, size="md")
        service("API", "99.99%", [120, 118, 124, 119, 121, 117, 122, 120,
                                  119, 118], "success", "circle-check")
        service("Dashboard", "99.95%", [210, 205, 214, 208, 212, 206, 209,
                                        215, 211, 207], "success", "circle-check")
        service("Webhooks", "99.21%", [180, 176, 190, 260, 340, 310, 220,
                                       195, 188, 182], "warning", "triangle-alert")
        service("Search", "97.80%", [90, 94, 92, 150, 420, 480, 390, 210,
                                     130, 96], "error", "circle-x")


def sizes() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center", align="end"):
        for size in ("xs", "sm", "md", "lg", "xl"):
            with ui.vstack(gap="xs", align="center"):
                ui.sparkline(data=[4, 6, 5, 8, 7, 10, 9, 12], size=size,
                             color="secondary", show_last_dot=True)
                ui.text(size, size="xs", color="muted")


def page() -> None:
    page_header("sparkline", "Sparkline", SUMMARY)
    example("KPI tiles", kpi_row, uses=[kpi], full=True,
            note="A list of numbers is enough. The area fill gives the tile "
                 "its colour without competing with the figure.")
    example("In a table", product_table, uses=[trend_cell], full=True,
            note="A column's render= returns the sparkline; the colour says "
                 "whether the product is climbing or falling.")
    example("A status list", status_list, uses=[service],
            note="Straight segments for raw measures: a spike stays a spike.")
    example("Sizes", sizes,
            note="Five sizes, and a last dot to mark where the series ends "
                 "today.")
