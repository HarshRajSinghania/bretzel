"""``/color-picker`` — a hex field with the theme's palette one click away."""

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A themable colour field: the palette of your theme in a panel, "
           "and any hex typed by hand.")


def brand_colour() -> None:
    with ui.form_field(label="Brand colour",
                       hint="Used for buttons and links in your emails.",
                       classes="w-full max-w-xs"):
        ui.color_picker(value="#2f5fd0")


def calendar_colours() -> None:
    with ui.card(padding="md", classes="w-full max-w-md"), ui.vstack(gap="md"):
        ui.heading("Calendars", level=3, size="md")
        with ui.grid(cols=2, gap="md"):
            with ui.form_field(label="Work"):
                ui.color_picker(value="#0f766e", name="work")
            with ui.form_field(label="Personal"):
                ui.color_picker(value="#c2410c", name="personal")
            with ui.form_field(label="Holidays"):
                ui.color_picker(value="", placeholder="No colour",
                                clearable=True, name="holidays")
            with ui.form_field(label="Shared with me",
                               hint="Set by the calendar owner."):
                ui.color_picker(value="#7c3aed", disabled=True, name="shared")


def sizes() -> None:
    with ui.vstack(gap="md", classes="w-full max-w-xs"):
        ui.color_picker(value="#e11d48", size="sm", name="size-sm")
        ui.color_picker(value="#2563eb", size="md", name="size-md")
        ui.color_picker(value="#16a34a", size="lg", name="size-lg")


class LabelDraft(PageState):
    name: str = field(default="Needs design review")
    colour: str = field(default="#d97706")


def update_label(draft: LabelDraft) -> None:
    """The new name or colour is already in ``draft``; the preview follows."""


@refreshable(deps=[LabelDraft])
def label_preview() -> None:
    draft = LabelDraft()
    with ui.hstack(gap="sm"):
        ui.icon("tag", size="lg", style=f"color: {draft.colour}")
        ui.text(draft.name or "Untitled label", weight="medium")
        ui.text(draft.colour, color="muted", size="sm", classes="font-mono")


def label_editor() -> None:
    draft = LabelDraft()
    with ui.card(padding="md", classes="w-full max-w-md"), ui.vstack(gap="md"):
        with ui.grid(cols=2, gap="md"):
            with ui.form_field(label="Label"):
                ui.input(value=draft.name, on_change=update_label)
            with ui.form_field(label="Colour"):
                ui.color_picker(value=draft.colour, color="secondary",
                                on_change=update_label)
        ui.divider()
        label_preview()


def page() -> None:
    page_header("color_picker", "Color picker", SUMMARY)
    example("A brand colour", brand_colour,
            note="The value is a hex string. The panel offers the named "
                 "colours of the active theme.")
    example("Calendar colours", calendar_colours,
            note="clearable with a placeholder for “no colour”, and disabled "
                 "for one the user cannot change.")
    example("Sizes", sizes)
    example("A label editor", label_editor,
            uses=[LabelDraft, update_label, label_preview],
            note="on_change sends the colour to Python, and the preview zone "
                 "re-renders with it.")
