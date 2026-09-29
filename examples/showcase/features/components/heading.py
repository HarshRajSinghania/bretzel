"""``/heading`` — the outline of a page, h1 to h6."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Six semantic levels, a visual size you can set apart from the "
           "level, and titles that follow the browser's state.")


def outline() -> None:
    with ui.vstack(gap="sm", classes="w-full max-w-lg"):
        ui.heading("Employee handbook", level=1)
        ui.heading("Working at Northwind", level=2)
        ui.heading("Time off and holidays", level=3)
        ui.heading("Requesting parental leave", level=4)
        ui.heading("Documents to provide", level=5)
        ui.heading("Proof of birth or adoption", level=6)


def hero() -> None:
    with ui.vstack(gap="md", align="center", classes="max-w-2xl"):
        ui.heading("Invoicing that closes the month for you", level=1,
                   size="4xl", weight="extrabold", classes="text-center")
        ui.text("Send, chase and reconcile every invoice from one screen.",
                size="lg", color="muted", align="center")
        ui.button("Start free trial", icon_right="arrow-right", size="lg")


def card_titles() -> None:
    with ui.grid(min_col="12rem", gap="md", classes="w-full"):
        for title, value, color in (("Monthly revenue", "€48,210", "primary"),
                                    ("Active customers", "1,284", "success"),
                                    ("Open tickets", "37", "warning")):
            with ui.card(padding="md"), ui.vstack(gap="xs"):
                ui.heading(title, level=3, size="sm", weight="medium",
                           color="muted")
                ui.heading(value, level=4, size="3xl", color=color)


def section_header() -> None:
    with ui.hstack(gap="md", justify="between", wrap=True, classes="w-full"):
        with ui.vstack(gap="none"):
            ui.heading("Team members", level=2, size="xl")
            ui.text("12 people have access to this workspace.", color="muted",
                    size="sm")
        ui.button("Invite people", icon_left="user-plus", variant="outline")


class Draft(ClientState):
    title: str = field(default="Q4 product roadmap")


def live_title() -> None:
    draft = Draft()
    with ui.vstack(gap="md", classes="w-full max-w-md"):
        ui.input(value=draft.title, placeholder="Untitled document",
                 icon_left="pencil")
        with ui.card(padding="md"), ui.vstack(gap="xs"):
            ui.text("Preview", size="xs", color="muted", weight="medium")
            ui.heading(draft.title, level=2, size="2xl")
            ui.text("Last edited by Maya Chen", size="sm", color="muted")


def page() -> None:
    page_header("heading", "Heading", SUMMARY)
    example("A document outline", outline,
            note="level= picks the tag, h1 to h6; each level gets its own size "
                 "from the theme.")
    example("A landing hero", hero,
            note="size= and weight= change the look without touching the "
                 "level the screen reader announces.")
    example("Card titles", card_titles, full=True,
            note="A small, muted h3 for the label and a large coloured value.")
    example("A section header", section_header, full=True)
    example("A title that follows the browser", live_title, uses=[Draft],
            note="Bind the text to a ClientState field: the heading follows "
                 "every keystroke, no request involved.")
