"""``/sidebar`` — the navigation column of an app.

In an app the sidebar fills the screen's height (the theme's root is
``h-screen``). Inside a preview box it must fill the BOX instead, hence
``slots={"root": "h-full!"}`` on every example: ``h-full!`` with
Tailwind's ``!`` is the override that wins over ``h-screen``.
"""

from functools import partial

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Sections, badges and an account menu at the foot — a column "
           "that folds to an icon rail or slides out of the way.")


def app_navigation() -> None:
    with ui.hstack(gap="none", align="stretch",
                   classes="h-[30rem] w-full [contain:inline-size] overflow-hidden "
                           "rounded-box border border-text/10"):
        with ui.sidebar(collapsible="rail", width="sm", slots={"root": "h-full!"}):
            ui.sidebar_title("Nimbus", icon=ui.icon("cloud", color="primary", size="lg"))
            with ui.sidebar_section(label="Workspace"):
                ui.sidebar_item("Dashboard", icon="layout-dashboard", active=True)
                ui.sidebar_item("Inbox", icon="inbox", badge=12)
                ui.sidebar_item("Projects", icon="folder-kanban")
                ui.sidebar_item("Calendar", icon="calendar")
            with ui.sidebar_section(label="Finance"):
                ui.sidebar_item("Invoices", icon="receipt", badge="3 due")
                ui.sidebar_item("Reports", icon="chart-line")
                ui.sidebar_item("Payroll", icon="banknote", disabled=True)
            with ui.sidebar_footer(
                name="Ada Lovelace", subtitle="ada@nimbus.io",
                avatar="https://i.pravatar.cc/96?u=ada",
            ):
                ui.sidebar_footer_item(label="Profile", icon_left="user")
                ui.sidebar_footer_item(label="Billing", icon_left="credit-card")
                ui.sidebar_footer_item(label="Log out", icon_left="log-out",
                                       color="error")
        with ui.pane(padding="lg", gap="md"):
            ui.heading("Good morning, Ada", level=3, size="xl")
            ui.text("Three invoices are due this week and 12 messages are "
                    "waiting in your inbox.", color="muted")
            with ui.grid(min_col="12rem", gap="md"):
                with ui.card(padding="md"), ui.vstack(gap="xs"):
                    ui.text("Revenue", size="sm", color="muted")
                    ui.heading("€48.2k", level=4, size="2xl")
                with ui.card(padding="md"), ui.vstack(gap="xs"):
                    ui.text("Open projects", size="sm", color="muted")
                    ui.heading("14", level=4, size="2xl")


def messages_in(folder: str) -> list[tuple[str, str]]:
    return {
        "inbox": [("Lumen Studio", "Brand guidelines, v3"),
                  ("Atlas Freight", "Your shipment left Rotterdam"),
                  ("Kinfolk & Co", "Invoice INV-2038 is paid")],
        "starred": [("Northwind Traders", "Renewal: the numbers you asked for")],
        "sent": [("Grace Hopper", "Re: onboarding checklist"),
                 ("Alan Turing", "Slides for Thursday")],
    }[folder]


class Mailbox(PageState):
    folder: str = field(default="inbox")


def open_folder(folder: str) -> None:
    Mailbox().folder = folder


@refreshable(deps=[Mailbox])
def mail_app() -> None:
    folder = Mailbox().folder
    with ui.hstack(gap="none", align="stretch",
                   classes="h-[22rem] w-full [contain:inline-size] overflow-hidden "
                           "rounded-box border border-text/10"):
        with (
            ui.sidebar(collapsible="none", width="sm", slots={"root": "h-full!"}),
            ui.sidebar_section(label="Mail"),
        ):
            ui.sidebar_item("Inbox", icon="inbox", badge=3,
                            active=folder == "inbox",
                            on_click=partial(open_folder, "inbox"))
            ui.sidebar_item("Starred", icon="star",
                            active=folder == "starred",
                            on_click=partial(open_folder, "starred"))
            ui.sidebar_item("Sent", icon="send",
                            active=folder == "sent",
                            on_click=partial(open_folder, "sent"))
        with ui.pane(padding="md", gap="sm"):
            ui.heading(folder.capitalize(), level=3, size="lg")
            for sender, subject in messages_in(folder):
                with ui.card(padding="sm"), ui.hstack(gap="sm"):
                    ui.avatar(name=sender, size="sm", color="secondary")
                    with ui.vstack(gap="none", classes="min-w-0"):
                        ui.text(sender, weight="medium", size="sm")
                        ui.text(subject, color="muted", size="sm", truncate=True)


def server_selection() -> None:
    mail_app()


def slide_away() -> None:
    with ui.hstack(gap="none", align="stretch",
                   classes="h-[22rem] w-full [contain:inline-size] overflow-hidden "
                           "rounded-box border border-text/10"):
        with ui.sidebar(collapsible="offcanvas", width="sm",
                        slots={"root": "h-full!"}) as nav:
            ui.sidebar_title("Docs", icon=ui.icon("book-open", color="primary",
                                                   size="lg"))
            with ui.sidebar_section(label="Guides"):
                ui.sidebar_item("Quickstart", icon="rocket", active=True)
                ui.sidebar_item("Authentication", icon="key-round")
                ui.sidebar_item("Webhooks", icon="webhook")
                ui.sidebar_item("Rate limits", icon="gauge")
        with ui.pane(padding="md", gap="md"):
            with ui.hstack(gap="sm"):
                ui.sidebar_trigger(nav, size="sm")
                ui.text("Guides / Quickstart", color="muted", size="sm")
            ui.heading("Quickstart", level=3, size="xl")
            ui.text("Create an API key, install the client, and send your "
                    "first request in under five minutes. Close the sidebar "
                    "to read with the full width.", color="muted")


def widths() -> None:
    with ui.hstack(gap="md", wrap=True, justify="center", align="start"):
        for width, label in (("sm", "Compact"), ("md", "Default"),
                             ("lg", "Roomy")):
            with (
                ui.hstack(gap="none", align="stretch",
                          classes="h-56 overflow-hidden rounded-box "
                                  "border border-text/10"),
                ui.sidebar(collapsible="none", width=width, slots={"root": "h-full!"}),
                ui.sidebar_section(label=label),
            ):
                ui.sidebar_item("Overview", icon="house", active=True)
                ui.sidebar_item("Customers", icon="users")
                ui.sidebar_item("Settings", icon="settings")


def page() -> None:
    page_header("sidebar", "Sidebar", SUMMARY)
    example("An app's navigation", app_navigation, full=True,
            note="Click the chevron beside the title, or the sidebar's right "
                 "edge: it folds to a rail of icons, and each label becomes "
                 "a tooltip. The account menu opens from the footer. In an "
                 "app the sidebar fills the screen's height; in a box like "
                 'this one, slots={"root": "h-full!"} makes it fill the box. '
                 "It is desktop navigation: on a phone, branch on "
                 "Screen().is_mobile and show a ui.bottom_bar instead.")
    example("A click that runs Python", server_selection,
            uses=[messages_in, Mailbox, open_folder, mail_app], full=True,
            note="Each item's on_click opens a folder on the server; the zone "
                 "re-renders with the new active row and its messages.")
    example("Slides out of the way", slide_away, full=True,
            note='collapsible="offcanvas" hides the whole column. '
                 "ui.sidebar_trigger is the button that brings it back — "
                 "put it wherever your top bar is.")
    example("Three widths", widths,
            note='width= sets the open width; collapsible="none" keeps the '
                 "column open for good.")
