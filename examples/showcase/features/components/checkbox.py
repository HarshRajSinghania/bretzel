"""``/checkbox`` — yes or no, one box at a time."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A box with its label, for consent, permissions and checklists — "
           "bound to state, it drives the rest of the page.")


class Consent(ClientState):
    accepted: bool = field(default=False)


def terms() -> None:
    consent = Consent()
    with ui.vstack(gap="md", classes="w-full max-w-sm"):
        ui.checkbox(checked=consent.accepted,
                    label="I have read and accept the Data Processing Agreement")
        ui.button("Activate integration", icon_left="plug", classes="w-full",
                  disabled=~consent.accepted)


def permissions() -> None:
    with ui.card(padding="md", classes="w-full max-w-sm"), ui.vstack(gap="sm"):
        ui.text("Omar can…", weight="semibold")
        ui.checkbox(label="View invoices and payments", checked=True)
        ui.checkbox(label="Create and send invoices", checked=True)
        ui.checkbox(label="Issue refunds")
        ui.checkbox(label="Export accounting data")
        ui.checkbox(label="Manage billing (owner only)", checked=True,
                    disabled=True)


class Onboarding(ClientState):
    profile: bool = field(default=True)
    invite: bool = field(default=False)
    domain: bool = field(default=False)
    payment: bool = field(default=False)


def checklist() -> None:
    steps = Onboarding()
    with ui.card(padding="md", classes="w-full max-w-sm"), ui.vstack(gap="md"):
        ui.heading("Get started", level=3, size="md")
        ui.progress(value=(steps.profile + steps.invite + steps.domain
                           + steps.payment) * 25,
                    color="success", size="sm")
        with ui.vstack(gap="sm"):
            ui.checkbox(checked=steps.profile, label="Complete your profile",
                        color="success")
            ui.checkbox(checked=steps.invite, label="Invite two teammates",
                        color="success")
            ui.checkbox(checked=steps.domain, label="Verify your domain",
                        color="success")
            ui.checkbox(checked=steps.payment, label="Add a payment method",
                        color="success")


def sizes_and_colors() -> None:
    with ui.vstack(gap="md"):
        with ui.hstack(gap="lg", wrap=True, justify="center"):
            for size in ("xs", "sm", "md", "lg", "xl"):
                ui.checkbox(label=f"Size {size}", size=size, checked=True)
        with ui.hstack(gap="lg", wrap=True, justify="center"):
            for color in ("primary", "secondary", "success", "warning", "error",
                          "info"):
                ui.checkbox(label=color.capitalize(), color=color, checked=True)


def page() -> None:
    page_header("checkbox", "Checkbox", SUMMARY)
    example("Consent before an action", terms, uses=[Consent],
            note="The box is bound to a ClientState, and the button's "
                 "disabled reads the opposite — no request, no JavaScript.")
    example("A list of permissions", permissions,
            note="A disabled box keeps its value visible: the owner's right "
                 "cannot be taken away here.")
    example("An onboarding checklist", checklist, uses=[Onboarding],
            note="The progress bar adds up four bound booleans in the "
                 "browser — tick a step and watch it move.")
    example("Sizes and colours", sizes_and_colors)
