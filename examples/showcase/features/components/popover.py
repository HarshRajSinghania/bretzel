"""``/popover`` — a small panel anchored to the element that opened it."""

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A floating panel anchored to its trigger — for an explanation, a "
           "profile card or a quick edit, without leaving the page.")


def explain_metric() -> None:
    with ui.card(padding="md", classes="w-full max-w-xs"), ui.vstack(gap="xs"):
        with ui.hstack(gap="xs"):
            ui.text("Net revenue retention", size="sm", color="muted")
            with ui.popover(trigger=ui.icon_button("info", variant="ghost",
                                                   size="xs", tooltip="About"),
                            position="top"), ui.vstack(gap="xs", classes="max-w-64"):
                ui.text("Net revenue retention", weight="semibold")
                ui.text("Revenue from last year's customers today, "
                        "divided by what they paid a year ago. Above "
                        "100 % means expansion beats churn.",
                        size="sm", color="muted")
        ui.heading("112 %", level=3, size="2xl")


def profile_card() -> None:
    with ui.hstack(gap="xs"):
        ui.text("Approved by", color="muted")
        margaret = ui.button("Margaret Hamilton", icon_left="at-sign", variant="ghost")
        with ui.popover(trigger=margaret), ui.vstack(gap="md", classes="w-64"):
            with ui.hstack(gap="sm"):
                ui.avatar(src="https://i.pravatar.cc/96?u=margaret", size="lg",
                          name="Margaret Hamilton", status="online")
                with ui.vstack(gap="none"):
                    ui.text("Margaret Hamilton", weight="semibold")
                    ui.text("Head of Engineering", size="sm", color="muted")
            ui.text("Boston · local time 10:42", size="sm", color="muted")
            with ui.hstack(gap="sm"):
                ui.button("Message", size="sm", icon_left="message-square")
                ui.button("Profile", size="sm", variant="outline")


class Board(PageState):
    title: str = field(default="Spring launch")


def rename_board(board: Board) -> None:
    board.title = str(board.title).strip() or "Untitled board"


@refreshable(deps=[Board])
def board_title() -> None:
    ui.heading(str(Board().title), level=3, size="lg")


def quick_edit() -> None:
    board = Board()
    with ui.hstack(gap="sm"):
        board_title()
        popover = ui.popover(trigger=ui.icon_button("pencil", variant="ghost",
                                                    size="sm", tooltip="Rename"))
        with popover, ui.form(on_submit=[rename_board, popover.close()]), ui.vstack(gap="sm"):
            with ui.form_field(label="Board name", classes="w-64"):
                ui.input(value=board.title, maxlength=60)
            with ui.hstack(gap="sm", justify="end"):
                ui.button("Cancel", size="sm", variant="ghost",
                          on_click=popover.close())
                ui.button("Save", size="sm", type="submit")


def positions() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        for position in ("top", "right", "bottom", "left"):
            with ui.popover(trigger=ui.button(position.capitalize(),
                                              variant="outline", size="sm"),
                            position=position):
                ui.text(f"Pinned to the {position}.", size="sm")


def page() -> None:
    page_header("popover", "Popover", SUMMARY)
    example("Explain a number", explain_metric,
            note="The trigger is any component, passed as trigger=. Click "
                 "outside or press Escape to close.")
    example("A profile card", profile_card,
            note="Anything can go inside: an avatar, text, buttons.")
    example("Edit in place", quick_edit, uses=[Board, rename_board, board_title],
            note="A form inside the popover: saving renames the board on the "
                 "server and closes the popover with popover.close().")
    example("Positions", positions,
            note="By default the popover takes the side with the most room; "
                 "position= pins it.")
