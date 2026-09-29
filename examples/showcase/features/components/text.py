"""``/text`` — every line of copy that is not a heading."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Ten sizes, four weights, every semantic colour, truncation — "
           "and text that follows the browser's state live.")


def type_scale() -> None:
    with ui.vstack(gap="xs"):
        for size in ("xs", "sm", "md", "lg", "xl", "2xl", "3xl"):
            with ui.hstack(gap="md", align="baseline"):
                ui.text(size, size="xs", color="muted", classes="w-8 font-mono")
                ui.text("Ship internal tools in days", size=size)


def status_messages() -> None:
    with ui.vstack(gap="sm"):
        ui.text("Payment received — invoice INV-2041 is settled.", color="success")
        ui.text("Your trial ends in 3 days.", color="warning", weight="medium")
        ui.text("The card ending in 4242 was declined.", color="error",
                weight="semibold")
        ui.text("Last synced 2 minutes ago.", color="muted", size="sm")


def pricing() -> None:
    with ui.card(padding="lg", classes="w-full max-w-xs"), ui.vstack(gap="sm"):
        ui.text("Team plan", weight="semibold", color="primary", size="sm")
        with ui.hstack(gap="sm", align="baseline"):
            ui.text("€19", size="4xl", weight="bold")
            ui.text("€29", size="lg", color="muted", decoration="line-through")
            ui.text("/ seat / month", color="muted", size="sm")
        ui.text("Billed yearly. Cancel any time.", size="sm", italic=True,
                color="muted")


FILES = ["Q3-board-meeting-minutes-final-v4-approved-by-legal.pdf",
         "customer-interviews-transcripts-september.docx",
         "brand-guidelines-2026.fig"]


def file_list() -> None:
    with ui.card(padding="md", classes="w-full max-w-sm"), ui.vstack(gap="sm"):
        for name in FILES:
            with ui.hstack(gap="sm", classes="min-w-0"):
                ui.icon("file-text", color="muted", size="sm")
                ui.text(name, truncate=True, size="sm", classes="min-w-0 flex-1")


def paragraph() -> None:
    with ui.vstack(gap="sm", classes="max-w-xl"):
        ui.text("Why we built Bretzel", tag="p", weight="semibold", align="center")
        ui.text("Most internal tools start as a spreadsheet and end as a "
                "React app nobody wants to maintain. Bretzel keeps the whole "
                "thing in Python: the state, the handlers and the interface.",
                tag="p", align="justify", color="muted")


class Workspace(ClientState):
    slug: str = field(default="northwind")


def live_text() -> None:
    workspace = Workspace()
    with ui.vstack(gap="sm", classes="w-full max-w-sm"):
        ui.text("Workspace name", size="sm", weight="medium")
        ui.input(value=workspace.slug, suffix=".bretzel.app")
        with ui.hstack(gap="xs"):
            ui.text("Your team will sign in at", size="sm", color="muted")
            ui.text(workspace.slug + ".bretzel.app", size="sm", weight="medium",
                    classes="font-mono")


def page() -> None:
    page_header("text", "Text", SUMMARY)
    example("Type scale", type_scale,
            note="One size scale for the whole app, repainted by the theme.")
    example("Status messages", status_messages,
            note="A colour says what happened; the weight says how much it matters.")
    example("A price, and the old one", pricing,
            note="Sizes, weights and a line-through combine into a pricing block.")
    example("Long names that truncate", file_list,
            note="truncate=True cuts with an ellipsis instead of breaking the row.")
    example("Paragraphs", paragraph,
            note="tag=\"p\" for real paragraphs; align= for centred or justified copy.")
    example("Text that follows the browser", live_text, uses=[Workspace],
            note="Pass a ClientState field instead of a string: the text follows "
                 "every keystroke, with no request to the server.")
