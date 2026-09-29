"""``/skeleton`` — the shape of what is about to load."""

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Grey shapes that hold the layout while data loads — lines, "
           "circles and blocks, sized like the real thing.")


def shapes() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center", align="center"):
        ui.skeleton(variant="circle", width="48px", height="48px")
        ui.skeleton(variant="text", width="160px")
        ui.skeleton(variant="rectangle", width="160px", height="80px")


def profile_card() -> None:
    with ui.card(padding="md", classes="w-full max-w-sm"), ui.vstack(gap="md"):
        with ui.hstack(gap="sm"):
            ui.skeleton(variant="circle", width="48px", height="48px")
            with ui.vstack(gap="xs", classes="flex-1"):
                ui.skeleton(variant="text", width="60%")
                ui.skeleton(variant="text", width="40%")
        ui.skeleton(variant="rectangle", width="100%", height="140px")
        ui.skeleton(variant="text", width="90%")
        ui.skeleton(variant="text", width="75%")


def table_rows() -> None:
    with ui.card(padding="md", classes="w-full max-w-xl"), ui.vstack(gap="md"):
        for _ in range(4):
            with ui.hstack(gap="md"):
                ui.skeleton(variant="circle", width="32px", height="32px")
                ui.skeleton(variant="text", width="35%")
                ui.skeleton(variant="text", width="20%")
                ui.skeleton(variant="rectangle", width="64px", height="22px")


def still() -> None:
    with ui.grid(cols=3, gap="md", classes="w-full max-w-xl"):
        for _ in range(3):
            with ui.card(padding="md"), ui.vstack(gap="sm"):
                ui.skeleton(variant="text", width="50%", animated=False)
                ui.skeleton(variant="rectangle", width="70%", height="28px",
                            animated=False)


class Article(PageState):
    loaded: bool = field(default=False)


def load_article() -> None:
    Article().loaded = True


def unload_article() -> None:
    Article().loaded = False


@refreshable(deps=[Article])
def article() -> None:
    loaded = Article().loaded
    with ui.vstack(gap="md", classes="w-full max-w-md"):
        with ui.card(padding="md"), ui.vstack(gap="sm"):
            if loaded:
                ui.heading("Closing the books in three days", level=3,
                           size="md")
                ui.text("How the finance team at Atlas Freight cut its "
                        "month-end from nine days to three, with one shared "
                        "checklist and no new software.", color="muted")
            else:
                ui.skeleton(variant="text", width="70%", height="1.5rem")
                ui.skeleton(variant="text", width="100%")
                ui.skeleton(variant="text", width="85%")
        if loaded:
            ui.button("Show the skeleton", variant="ghost", size="sm",
                      icon_left="rotate-ccw", on_click=unload_article,
                      classes="self-center")
        else:
            ui.button("Load the article", variant="soft", size="sm",
                      icon_left="download", on_click=load_article,
                      classes="self-center")


def loading_then_loaded() -> None:
    article()


def page() -> None:
    page_header("skeleton", "Skeleton", SUMMARY)
    example("Three shapes", shapes,
            note="A line of text, an avatar, a block — width and height take "
                 "any CSS length.")
    example("A profile card", profile_card,
            note="Mirror the layout that is coming, so nothing jumps when it "
                 "arrives.")
    example("Rows of a list", table_rows)
    example("Without the shimmer", still,
            note="animated=False for places where movement would distract.")
    example("Swapped for the real content", loading_then_loaded,
            uses=[Article, load_article, unload_article, article],
            note="The same zone renders the placeholder or the article, "
                 "depending on a server state.")
