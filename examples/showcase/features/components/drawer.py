"""``/drawer`` — a panel that slides in from an edge of the screen."""

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A panel that slides in from any edge — for details, filters and "
           "action sheets, without leaving the page.")


def order_details() -> None:
    drawer = ui.drawer(title="Order #10482", side="right", width="md")
    with drawer, ui.vstack(gap="md"):
        with ui.hstack(gap="sm"):
            ui.badge("Shipped", color="success", variant="soft",
                     icon_left="truck")
            ui.text("Placed on 12 March, 09:41", color="muted", size="sm")
        ui.divider()
        for item, price in (("Walnut desk organiser", "€64.00"),
                            ("Linen notebook × 3", "€36.00"),
                            ("Brass pen", "€48.00")):
            with ui.hstack(justify="between"):
                ui.text(item)
                ui.text(price, weight="medium")
        ui.divider()
        with ui.hstack(justify="between"):
            ui.text("Total", weight="semibold")
            ui.text("€148.00", weight="semibold")
        with ui.hstack(gap="sm", justify="end"):
            ui.button("Close", variant="ghost", on_click=drawer.close())
            ui.button("Download invoice", icon_left="download")
    ui.button("View order", variant="outline", icon_left="receipt",
              on_click=drawer.open())


def invoices() -> list[dict]:
    return [
        {"number": "INV-2041", "customer": "Northwind Traders", "status": "paid"},
        {"number": "INV-2040", "customer": "Lumen Studio", "status": "pending"},
        {"number": "INV-2039", "customer": "Atlas Freight", "status": "overdue"},
        {"number": "INV-2038", "customer": "Kinfolk & Co", "status": "paid"},
        {"number": "INV-2037", "customer": "Harbor Labs", "status": "overdue"},
        {"number": "INV-2036", "customer": "Oakline", "status": "pending"},
    ]


class Filters(PageState):
    status: str = field(default="all")


def apply_filters(filters: Filters) -> None:
    """The typed parameter already holds the submitted fields."""


@refreshable(deps=[Filters])
def invoice_list() -> None:
    status = str(Filters().status)
    rows = [row for row in invoices() if status in ("all", row["status"])]
    colors = {"paid": "success", "pending": "warning", "overdue": "error"}
    with ui.vstack(gap="sm", classes="w-full"):
        ui.text(f"{len(rows)} invoices · {status}", size="sm", color="muted")
        for row in rows:
            with ui.hstack(gap="md"):
                ui.text(row["number"], weight="medium", classes="font-mono")
                ui.text(row["customer"], color="muted", classes="flex-1")
                ui.badge(row["status"].capitalize(), color=colors[row["status"]],
                         variant="soft", size="sm")


def filters_drawer() -> None:
    filters = Filters()
    drawer = ui.drawer(title="Filter invoices", side="left", width="sm")
    with drawer, ui.form(on_submit=[apply_filters, drawer.close()]), ui.vstack(gap="md"):
        with ui.form_field(label="Status"), ui.radio_group(value=filters.status):
            ui.radio("all", label="All invoices")
            ui.radio("paid", label="Paid")
            ui.radio("pending", label="Pending")
            ui.radio("overdue", label="Overdue")
        ui.button("Show results", type="submit", icon_left="filter")
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="md"):
        with ui.hstack(justify="between"):
            ui.heading("Invoices", level=3, size="md")
            ui.button("Filters", size="sm", variant="outline",
                      icon_left="sliders-horizontal", on_click=drawer.open())
        invoice_list()


def share_sheet() -> None:
    sheet = ui.drawer(title="Share “Q3 planning”", side="bottom", width="sm")
    with sheet, ui.hstack(gap="sm", wrap=True, justify="center"):
        ui.button("Copy link", icon_left="link", variant="soft",
                  on_click=sheet.close())
        ui.button("Email", icon_left="mail", variant="soft",
                  on_click=sheet.close())
        ui.button("Slack", icon_left="message-square", variant="soft",
                  on_click=sheet.close())
        ui.button("Export PDF", icon_left="file-down", variant="soft",
                  on_click=sheet.close())
    ui.button("Share", icon_left="share-2", on_click=sheet.open())


def notice_bar() -> None:
    notice = ui.drawer(title="Scheduled maintenance", side="top", width="sm")
    with notice, ui.vstack(gap="sm", align="center"):
        ui.text("Billing will be read-only on Sunday from 02:00 to 04:00 "
                "UTC while we move to the new region.", color="muted",
                align="center")
        ui.button("Understood", size="sm", on_click=notice.close())
    ui.button("Show the notice", variant="outline", icon_left="megaphone",
              on_click=notice.open())


def widths() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        for width in ("sm", "md", "lg", "xl"):
            with ui.drawer(title=f"Width {width}", width=width) as drawer:
                ui.text("Wide enough for a comment thread, narrow enough to "
                        "keep the page behind it in view.", color="muted")
            ui.button(f"Width {width}", variant="outline", on_click=drawer.open())


def page() -> None:
    page_header("drawer", "Drawer", SUMMARY)
    example("Details on the side", order_details,
            note="Opened with drawer.open(), closed by the × button, the "
                 "backdrop, Escape, or any drawer.close() inside it.")
    example("Filters that run on the server", filters_drawer,
            uses=[invoices, Filters, apply_filters, invoice_list],
            note="The drawer holds a form: submitting filters the list on the "
                 "server and closes the drawer in the same click.")
    example("An action sheet from the bottom", share_sheet,
            note="On top and bottom drawers, width= sets the height.")
    example("A notice from the top", notice_bar)
    example("Widths", widths, note="sm, md (the default), lg and xl.")
