"""``/breadcrumb`` — where the reader is, and the way back up."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("The trail from the top of the app to the current page — each "
           "parent a link, the last segment where you are.")


def trail() -> None:
    ui.breadcrumb([
        {"label": "Workspace", "href": "#workspace"},
        {"label": "Projects", "href": "#projects"},
        {"label": "Website redesign"},
    ])


def with_icons() -> None:
    with ui.breadcrumb():
        ui.breadcrumb_item("Home", icon="house", href="#home")
        ui.breadcrumb_item("Customers", icon="building-2", href="#customers")
        ui.breadcrumb_item("Northwind Traders", icon="briefcase", href="#northwind")
        ui.breadcrumb_item("Invoice INV-2041", icon="receipt")


def separators() -> None:
    with ui.vstack(gap="md", align="center"):
        for separator in ("chevron-right", "/", "·"):
            ui.breadcrumb([("Docs", "#docs"), ("Components", "#components"),
                           "Breadcrumb"], separator=separator)


def sizes_and_colors() -> None:
    with ui.vstack(gap="md", align="center"):
        for size in ("xs", "sm", "md", "lg"):
            ui.breadcrumb([("Settings", "#settings"), ("Team", "#team"),
                           "Permissions"], size=size)
        ui.breadcrumb([("Settings", "#settings"), ("Team", "#team"),
                       "Permissions"], color="primary")


def page_heading() -> None:
    with ui.vstack(gap="sm", classes="w-full"):
        with ui.breadcrumb():
            ui.breadcrumb_item("Accounts", icon="building-2", href="#accounts")
            ui.breadcrumb_item("Atlas Freight", href="#atlas")
            ui.breadcrumb_item("Contracts")
        with ui.hstack(gap="md", justify="between", wrap=True):
            with ui.vstack(gap="none"):
                ui.heading("Contracts", level=2, size="2xl")
                ui.text("3 active · renewal due in 42 days", color="muted")
            with ui.hstack(gap="sm"):
                ui.button("Export", variant="outline", icon_left="download")
                ui.button("New contract", icon_left="plus")


def page() -> None:
    page_header("breadcrumb", "Breadcrumb", SUMMARY)
    example("A trail from a list", trail,
            note="Dicts, (label, href) tuples or plain strings. The last "
                 "segment is always the current page.")
    example("With icons", with_icons,
            note="ui.breadcrumb_item when a segment needs more than text.")
    example("Separators", separators,
            note="An icon name, or any literal text.")
    example("Sizes and colour", sizes_and_colors,
            note="The trail inherits the text colour; color= gives it an accent.")
    example("Above a page title", page_heading, full=True)
