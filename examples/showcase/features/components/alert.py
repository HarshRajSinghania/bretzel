"""``/alert`` — a message that sits in the flow of the page."""

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Four semantic tones, an optional title, an icon that picks "
           "itself — and a close button that can call Python.")


def statuses() -> None:
    with ui.vstack(gap="sm", classes="w-full max-w-xl"):
        ui.alert("Your workspace will be migrated to the new region on "
                 "Sunday at 02:00 UTC.", title="Scheduled maintenance",
                 color="info")
        ui.alert("Payment received. Invoice INV-2041 is now marked as paid.",
                 title="All settled", color="success")
        ui.alert("You have used 92% of your monthly API quota.",
                 title="Approaching your limit", color="warning")
        ui.alert("We could not charge the card ending in 4242. "
                 "Update it to keep your plan active.",
                 title="Payment failed", color="error")


def message_only() -> None:
    with ui.vstack(gap="sm", classes="w-full max-w-xl"):
        ui.alert("Changes are saved automatically as you type.", color="info")
        ui.alert("Two-factor authentication is on for every admin.",
                 color="success")
        ui.alert("This link expires in 24 hours.", color="warning")


def custom_icons() -> None:
    with ui.vstack(gap="sm", classes="w-full max-w-xl"):
        ui.alert("Invite three teammates this week and get a month of Pro.",
                 title="Better together", color="primary", icon="gift")
        ui.alert("Keyboard shortcuts are available — press ? to see them.",
                 color="secondary", icon="keyboard")
        ui.alert("Archived projects are read-only. Restore one to edit it.",
                 color="muted", icon=False)


def in_a_form() -> None:
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="md"):
        with ui.vstack(gap="xs"):
            ui.heading("Billing details", level=3, size="md")
            ui.text("Used on every invoice we send you.", color="muted",
                    size="sm")
        ui.alert("The card on file expires in 12 days.", color="warning",
                 icon="credit-card")
        with ui.form_field(label="Company name"):
            ui.input(value="Northwind Traders")
        with ui.form_field(label="VAT number"):
            ui.input(value="FR 40 303 265 045")
        with ui.hstack(gap="sm", justify="end"):
            ui.button("Cancel", variant="ghost")
            ui.button("Save details")


class Tips(PageState):
    hidden: bool = field(default=False)


def hide_tip() -> None:
    Tips().hidden = True


def show_tip() -> None:
    Tips().hidden = False


@refreshable(deps=[Tips])
def onboarding_tip() -> None:
    if Tips().hidden:
        ui.button("Show the tip again", icon_left="lightbulb", variant="ghost",
                  on_click=show_tip)
    else:
        ui.alert("Drag a card onto another column to change its status.",
                 title="Tip", color="info", icon="lightbulb",
                 dismissible=True, on_close=hide_tip, classes="w-full max-w-xl")


def dismissible() -> None:
    onboarding_tip()


def page() -> None:
    page_header("alert", "Alert", SUMMARY)
    example("Status messages", statuses,
            note="Info, success, warning and error each bring their own icon.")
    example("Just a message", message_only,
            note="Without a title, an alert is a single quiet line.")
    example("Your own icon and tone", custom_icons,
            note="icon= takes any Lucide name, or False for none; the "
                 "neutral colours suit promotions and hints.")
    example("Inside a form", in_a_form,
            note="Next to the fields it concerns, where the user is already "
                 "looking.")
    example("Dismissed on the server", dismissible,
            uses=[Tips, hide_tip, show_tip, onboarding_tip],
            note="on_close runs a Python function: here it remembers the "
                 "choice, and the zone re-renders without the tip.")
