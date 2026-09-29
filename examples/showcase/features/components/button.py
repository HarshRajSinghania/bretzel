"""``/button`` — the action everyone clicks first."""

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Five variants, every semantic colour, five sizes — and a click "
           "that runs Python.")


def variants() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        ui.button("Solid")
        ui.button("Soft", variant="soft")
        ui.button("Surface", variant="surface")
        ui.button("Outline", variant="outline")
        ui.button("Ghost", variant="ghost")


def colors() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        for color in ("primary", "secondary", "success", "warning", "error", "info"):
            ui.button(color.capitalize(), color=color)


def sizes() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        for size in ("xs", "sm", "md", "lg", "xl"):
            ui.button(f"Size {size}", size=size)


def with_icons() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        ui.button("Download report", icon_left="download", variant="outline")
        ui.button("Continue", icon_right="arrow-right")
        ui.button("Share", icon_left="share-2", variant="soft", color="secondary")
        ui.button("Delete", icon_left="trash-2", variant="soft", color="error")


def form_footer() -> None:
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="md"):
        with ui.vstack(gap="xs"):
            ui.heading("Delete this project?", level=3, size="md")
            ui.text("The 14 boards and their history go with it. "
                    "This cannot be undone.", color="muted", size="sm")
        with ui.hstack(gap="sm", justify="end"):
            ui.button("Cancel", variant="ghost")
            ui.button("Delete project", color="error", icon_left="trash-2")


class Votes(PageState):
    up: int = field(default=12)


def vote() -> None:
    Votes().up += 1


@refreshable(deps=[Votes])
def vote_button() -> None:
    ui.button(f"Upvote · {Votes().up}", icon_left="thumbs-up", variant="soft",
              on_click=vote)


def server_click() -> None:
    vote_button()


def states() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        ui.button("Saving…", loading=True)
        ui.button("Unavailable", disabled=True)
        ui.button("Read the docs", href="https://docs.bretzel-py.dev",
                  external=True, variant="outline", icon_right="external-link")


def page() -> None:
    page_header("button", "Button", SUMMARY)
    example("Variants", variants,
            note="Solid for the one action that matters, softer variants for "
                 "the ones around it.")
    example("Colours", colors,
            note="Every semantic colour of the theme; the text on the fill is "
                 "derived to stay readable.")
    example("Sizes", sizes)
    example("With icons", with_icons)
    example("In a confirmation", form_footer,
            note="A quiet way out, and the destructive action said in red.")
    example("A click that runs Python", server_click, uses=[Votes, vote, vote_button],
            note="on_click takes a Python function. The state changes on the "
                 "server, and only the zone that reads it is re-rendered.")
    example("Loading, disabled, link", states)
