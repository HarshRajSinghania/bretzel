"""``/dropdown`` — a menu of actions behind one button."""

from functools import partial

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A menu anchored to its trigger — icons, shortcuts, links, "
           "coloured rows, and items that run Python.")


def row_actions() -> None:
    with ui.card(padding="sm", classes="w-full max-w-md"), ui.hstack(justify="between"):
        with ui.hstack(gap="sm"):
            ui.icon("file-text", color="primary")
            with ui.vstack(gap="none"):
                ui.text("Q3 board report.pdf", weight="medium")
                ui.text("2.4 MB · edited 3 hours ago", size="sm", color="muted")
        with ui.dropdown(trigger=ui.icon_button("ellipsis", variant="ghost",
                                                size="sm", tooltip="Actions"),
                         align="end"):
            ui.dropdown_item(label="Open", icon_left="external-link",
                             shortcut="↵")
            ui.dropdown_item(label="Rename", icon_left="pencil", shortcut="F2")
            ui.dropdown_item(label="Duplicate", icon_left="copy", shortcut="Ctrl D")
            ui.dropdown_item(label="Download", icon_left="download")
            ui.dropdown_item(label="Move to trash", icon_left="trash-2",
                             color="error", shortcut="Del")


def account_menu() -> None:
    with ui.dropdown(trigger=ui.button("Grace Hopper", icon_left="circle-user-round",
                                       icon_right="chevron-down", variant="ghost"),
                     align="end"):
        ui.dropdown_item(label="Profile", icon_left="user", href="#profile")
        ui.dropdown_item(label="Billing", icon_left="credit-card", href="#billing")
        ui.dropdown_item(label="Team settings", icon_left="users", href="#team")
        ui.dropdown_item(label="Keyboard shortcuts", icon_left="keyboard",
                         shortcut="?")
        ui.dropdown_item(label="Sign out", icon_left="log-out", href="#sign-out")


class Invoice(PageState):
    status: str = field(default="sent")


def set_status(status: str) -> None:
    Invoice().status = status


@refreshable(deps=[Invoice])
def invoice_status() -> None:
    label, color = {"sent": ("Sent", "info"), "paid": ("Paid", "success"),
                    "void": ("Void", "error")}[str(Invoice().status)]
    with ui.hstack(gap="md"):
        ui.text("INV-2041 · Northwind Traders", weight="medium")
        ui.badge(label, color=color, variant="soft")


def change_status() -> None:
    menu = ui.button("Change status", icon_right="chevron-down", variant="outline",
                     size="sm")
    with ui.card(padding="sm", classes="w-full max-w-lg"), ui.hstack(justify="between"):
        invoice_status()
        with ui.dropdown(trigger=menu, align="end"):
            ui.dropdown_item(label="Mark as paid", icon_left="circle-check",
                             color="success", on_click=partial(set_status, "paid"))
            ui.dropdown_item(label="Back to sent", icon_left="send",
                             on_click=partial(set_status, "sent"))
            ui.dropdown_item(label="Send a reminder", icon_left="bell-ring",
                             color="warning", disabled=True)
            ui.dropdown_item(label="Void the invoice", icon_left="ban",
                             color="error", on_click=partial(set_status, "void"))


def placement() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        for position, align in (("bottom", "start"), ("bottom", "end"),
                                ("top", "start"), ("top", "end")):
            with ui.dropdown(trigger=ui.button(f"{position} · {align}",
                                               variant="soft", size="sm"),
                             position=position, align=align):
                ui.dropdown_item(label="Last 7 days")
                ui.dropdown_item(label="Last 30 days")
                ui.dropdown_item(label="This quarter")


def page() -> None:
    page_header("dropdown", "Dropdown", SUMMARY)
    example("Row actions", row_actions,
            note="An icon button as trigger, shortcuts on the right, and the "
                 "destructive action in red at the bottom.")
    example("Account menu", account_menu,
            note="Items with href= are links; align=\"end\" keeps the menu "
                 "under the right edge of its trigger.")
    example("Items that run Python", change_status,
            uses=[Invoice, set_status, invoice_status],
            note="on_click takes a handler (here a partial): the menu closes, "
                 "the state changes on the server, the badge re-renders.")
    example("Placement", placement,
            note="position picks the side, align the edge. By default the "
                 "menu takes the side with the most room.")
