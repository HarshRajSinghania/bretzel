"""``/empty-state`` — what to show when there is nothing to show."""

import functools

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("The screen before the first record: an icon, a sentence, and the "
           "one action that fills it.")


def first_run() -> None:
    with ui.empty_state("No projects yet", icon="folder-kanban",
                        description="Projects group your boards, files and "
                                    "people. Start with one — you can import "
                                    "the rest later."):
        ui.button("New project", icon_left="plus")
        ui.button("Import from Trello", variant="outline", icon_left="download")


def no_results() -> None:
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="md"):
        ui.input(value="invoice march atlas", icon_left="search")
        with ui.empty_state("No matching invoices", icon="search-x", size="sm",
                            color="muted",
                            description="Try fewer words, or search every "
                                        "workspace instead of this one."):
            ui.button("Clear search", variant="ghost", size="sm")


def all_done() -> None:
    ui.empty_state("You're all caught up", icon="circle-check", color="success",
                   description="No reviews are waiting for you. New requests "
                               "will show up here.")


def sizes() -> None:
    with ui.grid(min_col="12rem", gap="md", classes="w-full"):
        with ui.card(padding="md"):
            ui.empty_state("No comments", icon="message-square", size="xs",
                           description="Be the first to say something.")
        with ui.card(padding="md"):
            ui.empty_state("No files", icon="paperclip", size="md",
                           color="secondary",
                           description="Drop a PDF or an image here.")
        with ui.card(padding="md"):
            ui.empty_state("No alerts", icon="bell-off", size="lg",
                           color="info",
                           description="Monitors are quiet.")


def default_tasks() -> list[str]:
    return ["Send the Q3 report to Lumen Studio", "Renew the SSL certificate",
            "Review Grace's pull request"]


class Tasks(PageState):
    todo: list[str] = field(default_factory=default_tasks)


def complete(task: str) -> None:
    tasks = Tasks()
    tasks.todo = [t for t in tasks.todo if t != task]


def restore_tasks() -> None:
    Tasks().todo = default_tasks()


@refreshable(deps=[Tasks])
def task_list() -> None:
    tasks = Tasks().todo
    with ui.card(padding="md", classes="w-full max-w-md"), ui.vstack(gap="sm"):
        ui.heading("Today", level=3, size="md")
        for task in tasks:
            with ui.hstack(gap="sm", justify="between"):
                ui.text(task)
                ui.button("Done", size="xs", variant="soft", icon_left="check",
                          on_click=functools.partial(complete, task))
        if not tasks:
            with ui.empty_state("Nothing left for today", icon="party-popper",
                                size="sm", color="success",
                                description="Enjoy the quiet."):
                ui.button("Bring my tasks back", size="sm", variant="ghost",
                          on_click=restore_tasks)


def live_list() -> None:
    task_list()


def page() -> None:
    page_header("empty_state", "Empty state", SUMMARY)
    example("First run", first_run,
            note="Say what belongs here and offer the way to add it. "
                 "Buttons placed inside line up under the text.")
    example("No search results", no_results,
            note="Smaller and muted inside a panel — and a way back.")
    example("Nothing left to do", all_done,
            note="Emptiness can be good news: say it in green.")
    example("Sizes and colours", sizes, full=True)
    example("When the last item goes", live_list,
            uses=[default_tasks, Tasks, complete, restore_tasks, task_list],
            note="Complete each task: the server state empties, and the same "
                 "zone renders the empty state in its place.")
