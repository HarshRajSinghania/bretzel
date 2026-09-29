"""``/spinner`` — something is happening."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A rotating ring for the moments you cannot measure — five sizes, "
           "every colour, at home next to a line of text.")


def sizes() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center", align="center"):
        for size in ("xs", "sm", "md", "lg", "xl"):
            ui.spinner(size=size)


def colors() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center", align="center"):
        for color in ("primary", "secondary", "success", "warning", "error",
                      "info", "muted"):
            ui.spinner(color=color, size="lg")


def inline() -> None:
    with ui.vstack(gap="sm"):
        with ui.hstack(gap="sm"):
            ui.spinner(size="sm")
            ui.text("Syncing 3 calendars…")
        with ui.hstack(gap="sm"):
            ui.spinner(size="sm", color="muted")
            ui.text("Checking the domain's DNS records", color="muted")
        with ui.hstack(gap="sm"):
            ui.spinner(size="sm", color="success")
            ui.text("Deploying to production · step 2 of 3")


def loading_panel() -> None:
    with (ui.card(padding="lg", classes="w-full max-w-md"),
          ui.vstack(gap="sm", align="center", classes="py-6")):
        ui.spinner(size="xl")
        ui.text("Crunching last month's numbers", weight="medium")
        ui.text("This usually takes a few seconds.", color="muted", size="sm")


def in_a_button() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        ui.button("Publishing…", loading=True)
        ui.button("Uploading", loading=True, variant="outline")
        ui.icon_button("refresh-cw", loading=True, variant="soft",
                       tooltip="Refreshing")


def page() -> None:
    page_header("spinner", "Spinner", SUMMARY)
    example("Sizes", sizes)
    example("Colours", colors)
    example("Next to a status line", inline,
            note="Small and in the same colour as the text, it says the work "
                 "is ongoing without drawing the eye.")
    example("A loading panel", loading_panel,
            note="Centred, larger, with a sentence that sets expectations.")
    example("Inside a button", in_a_button,
            note="loading=True on a button or an icon button draws the same "
                 "spinner for you.")
