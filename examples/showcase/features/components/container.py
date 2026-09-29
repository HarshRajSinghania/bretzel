"""``/container`` — a centred column that stops growing."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A centred column with a maximum width and page padding — so a "
           "form or an article never stretches across a wide screen.")


def settings() -> None:
    with ui.container(width="sm"), ui.card(padding="lg"), ui.vstack(gap="md"):
        with ui.vstack(gap="xs"):
            ui.heading("Workspace", level=3, size="lg")
            ui.text("How your team and your customers see this workspace.",
                    color="muted", size="sm")
        with ui.form_field(label="Name"):
            ui.input(value="Northwind Traders")
        with ui.form_field(label="Address", hint="Letters, digits and dashes."):
            ui.input(value="northwind", prefix="app.northwind.io/")
        with ui.hstack(gap="sm", justify="end"):
            ui.button("Cancel", variant="ghost")
            ui.button("Save changes")


def article() -> None:
    with ui.container(width="sm"), ui.vstack(gap="md"):
        ui.text("Product update · September 2026", size="sm", color="primary",
                weight="medium")
        ui.heading("Recurring invoices are here", level=2, size="2xl")
        ui.text("Set a schedule once and every invoice goes out on time, "
                "numbered, with the right tax rate for each customer. Paused "
                "customers are skipped, and a failed card payment is retried "
                "three times before anyone gets an email.")
        ui.text("Around 65 characters per line is where reading is most "
                "comfortable; a container keeps long copy in that range "
                "however wide the window is.", color="muted")


def width_row(width: str, size: str) -> None:
    with (ui.container(width=width), ui.card(padding="sm"),
          ui.hstack(justify="between")):
        ui.text(f'width="{width}"', size="sm", weight="medium",
                classes="font-mono")
        ui.text(size, size="sm", color="muted")


def widths() -> None:
    with ui.vstack(gap="none", classes="w-full"):
        width_row("sm", "max 42rem")
        width_row("md", "max 48rem")
        width_row("full", "no maximum")


def page() -> None:
    page_header("container", "Container", SUMMARY)
    example("A settings page", settings, full=True,
            note="The form stays a comfortable width and centred, whatever "
                 "the size of the window.")
    example("A readable article", article, full=True)
    example("Width scale", widths, uses=[width_row], full=True,
            note="Five clamps from sm to 2xl, plus full; the padding is part "
                 "of the container.")
