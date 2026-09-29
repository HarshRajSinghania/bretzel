"""``/resizable`` — panels split by handles you drag."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Panels split by handles you drag. The split is kept in "
           "proportions, so it survives any window size.")


def mail_client() -> None:
    with ui.resizable(sizes=[20, 35, 45], classes="h-80 overflow-hidden rounded-box "
                                                  "border border-text/10"):
        with ui.resizable_panel(min_size=15), ui.vstack(gap="xs", classes="p-4"):
            ui.text("Folders", weight="semibold", size="sm")
            for folder, icon in (("Inbox", "inbox"), ("Starred", "star"),
                                 ("Sent", "send"), ("Archive", "archive")):
                with ui.hstack(gap="sm"):
                    ui.icon(icon, size="sm", color="muted")
                    ui.text(folder, size="sm", truncate=True)
        with ui.resizable_panel(min_size=25), ui.vstack(gap="sm", classes="p-4"):
            for sender, subject in (("Lumen Studio", "Brand guidelines, v3"),
                                    ("Atlas Freight", "Shipment left Rotterdam"),
                                    ("Kinfolk & Co", "INV-2038 is paid")):
                with ui.vstack(gap="none"):
                    ui.text(sender, weight="medium", size="sm", truncate=True)
                    ui.text(subject, color="muted", size="sm", truncate=True)
        with ui.resizable_panel(min_size=30), ui.vstack(gap="sm", classes="p-4"):
            ui.heading("Brand guidelines, v3", level=3, size="md")
            ui.text("Hi Ada — attached is the third round. We tightened the "
                    "logo's clear space, dropped the second accent colour, "
                    "and added a dark-mode palette for the app.",
                    color="muted", size="sm")


def editor_and_terminal() -> None:
    with ui.resizable(orientation="vertical", sizes=[65, 35],
                      classes="h-96 overflow-hidden rounded-box "
                              "border border-text/10"):
        with ui.resizable_panel(min_size=30):
            ui.code("from bretzel import ui\n\n\n"
                    "def invoice_total(lines):\n"
                    "    return sum(line.qty * line.price for line in lines)\n",
                    lang="python", classes="h-full")
        with ui.resizable_panel(min_size=15):
            ui.code("$ pytest tests/billing\n"
                    "........................ 24 passed in 1.42s",
                    lang="console", classes="h-full")


def fold_away() -> None:
    with ui.resizable(sizes=[30, 70], gap="sm", classes="h-56"):
        with (
            ui.resizable_panel(min_size=20, collapsible=True),
            ui.card(padding="md", classes="h-full"),
            ui.vstack(gap="xs"),
        ):
            ui.text("Outline", weight="semibold", size="sm")
            for heading in ("Summary", "Pricing", "Timeline", "Risks"):
                ui.text(heading, color="muted", size="sm", truncate=True)
        with (
            ui.resizable_panel(),
            ui.card(padding="md", classes="h-full"),
            ui.vstack(gap="xs"),
        ):
            ui.heading("Proposal for Atlas Freight", level=3, size="md")
            ui.text("Double-click the handle to fold the outline away; do it "
                    "again to bring it back.", color="muted", size="sm")


class Reader(ClientState, persist="local"):
    split: list = field(default_factory=lambda: [40, 60])


def remembered_split() -> None:
    reader = Reader()
    with ui.vstack(gap="md", classes="w-full"):
        with ui.resizable(sizes=reader.split, size="lg", color="secondary",
                          classes="h-48") as panes:
            with (
                ui.resizable_panel(min_size=20),
                ui.card(padding="md", classes="h-full"),
                ui.vstack(gap="xs"),
            ):
                ui.text("Contract — section 4", weight="semibold", size="sm")
                ui.text("The supplier delivers within ten working days of each order.",
                        color="muted", size="sm")
            with (
                ui.resizable_panel(min_size=20),
                ui.card(padding="md", classes="h-full"),
                ui.vstack(gap="xs"),
            ):
                ui.text("Comments", weight="semibold", size="sm")
                ui.text("Grace: can we make it seven? Atlas agreed to seven last year.",
                        color="muted", size="sm")
        with ui.hstack(gap="sm", justify="center"):
            ui.button("Focus on comments", variant="outline", size="sm",
                      on_click=panes.set([25, 75]))
            ui.button("Side by side", variant="ghost", size="sm",
                      on_click=panes.reset())


def page() -> None:
    page_header("resizable", "Resizable", SUMMARY)
    example("A mail client", mail_client, full=True,
            note="Three panels, each with a min_size in percent so no column "
                 "can be crushed. Drag the handles, or focus one and use the "
                 "arrow keys.")
    example("Editor over terminal", editor_and_terminal, full=True,
            note='orientation="vertical" stacks the panels.')
    example("A panel that folds away", fold_away, full=True,
            note="collapsible=True lets a double-click on the handle close the "
                 "panel, and gap= leaves room around the handle.")
    example("A split that survives a reload", remembered_split, uses=[Reader],
            full=True,
            note='sizes= is tied to a ClientState with persist="local": drag, '
                 "reload the page, and the split is where you left it. The "
                 "buttons use the imperative .set() and .reset().")
