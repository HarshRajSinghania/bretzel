"""``/accordion`` — sections that fold away."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Collapsible sections — one open at a time or several, with "
           "icons, a remembered state and commands to fold them all.")


def faq() -> None:
    with ui.accordion(value="trial", collapsible=True, classes="w-full max-w-xl"):
        with ui.accordion_item("trial", label="How long is the free trial?"):
            ui.text("Fourteen days, with every feature of the Team plan. No "
                    "card is needed to start.", color="muted")
        with ui.accordion_item("cancel", label="Can I cancel at any time?"):
            ui.text("Yes. You keep access until the end of the billing "
                    "period, and you can export all your data first.",
                    color="muted")
        with ui.accordion_item("vat", label="Do your prices include VAT?"):
            ui.text("Prices are shown without VAT. It is added at checkout "
                    "based on your billing country.", color="muted")
        with ui.accordion_item("seats", label="What counts as a seat?"):
            ui.text("Anyone who can sign in. Customers who only receive "
                    "invoices are free.", color="muted")


def settings() -> None:
    with ui.accordion(value=["profile", "notifications"], multiple=True,
                      classes="w-full max-w-xl"):
        with (ui.accordion_item("profile", label="Profile", icon="user"),
              ui.vstack(gap="sm")):
            with ui.form_field(label="Display name"):
                ui.input(value="Lena Park")
            with ui.form_field(label="Job title"):
                ui.input(value="Head of Finance")
        with (ui.accordion_item("notifications", label="Notifications",
                                icon="bell"),
              ui.vstack(gap="sm")):
            ui.switch(label="Email me when an invoice is paid", checked=True,
                      name="notify_paid")
            ui.switch(label="Weekly revenue digest", checked=False,
                      name="notify_digest")
        with ui.accordion_item("security", label="Security", icon="shield"):
            ui.button("Enable two-factor authentication", icon_left="key-round",
                      variant="outline")
        with ui.accordion_item("sso", label="Single sign-on · Scale plan",
                               icon="lock", disabled=True):
            ui.text("Available on the Scale plan.", color="muted")


class Checkout(ClientState, persist="local"):
    step: str = field(default="shipping")


def remembered() -> None:
    with ui.accordion(value=Checkout().step, collapsible=True,
                      color="secondary", classes="w-full max-w-xl"):
        with ui.accordion_item("shipping", label="Shipping address",
                               icon="truck"):
            ui.text("Ada Lovelace · 12 Rue de la Paix, 75002 Paris",
                    color="muted")
        with ui.accordion_item("delivery", label="Delivery", icon="package"):
            ui.text("Standard, 2 to 3 working days — free.", color="muted")
        with ui.accordion_item("payment", label="Payment", icon="credit-card"):
            ui.text("Visa ending in 4242, expires 08/28.", color="muted")


def commands() -> None:
    with ui.vstack(gap="md", classes="w-full max-w-xl"):
        with ui.accordion(value=["changelog-2"], multiple=True, size="sm") as changelog:
            with ui.accordion_item("changelog-3", label="v2.4 — Recurring invoices"):
                ui.text("Schedules, automatic numbering, retry on failed "
                        "payments.", color="muted", size="sm")
            with ui.accordion_item("changelog-2", label="v2.3 — Credit notes"):
                ui.text("Refund part of an invoice and keep the ledger "
                        "balanced.", color="muted", size="sm")
            with ui.accordion_item("changelog-1", label="v2.2 — Team roles"):
                ui.text("Viewer, editor and admin, per workspace.",
                        color="muted", size="sm")
        with ui.hstack(gap="sm"):
            ui.button("Expand all", icon_left="chevrons-up-down",
                      variant="outline", size="sm",
                      on_click=changelog.expand_all())
            ui.button("Collapse all", icon_left="chevrons-down-up",
                      variant="ghost", size="sm",
                      on_click=changelog.collapse_all())


def page() -> None:
    page_header("accordion", "Accordion", SUMMARY)
    example("Frequently asked questions", faq,
            note="One section open at a time; collapsible=True lets the open "
                 "one close too.")
    example("Settings, several open at once", settings,
            note="multiple=True takes a list of open sections. Items carry "
                 "an icon, and one is disabled.")
    example("Remember what was open", remembered, uses=[Checkout],
            note="value= bound to a ClientState with persist=\"local\": "
                 "open a section, reload the page, it is still open.")
    example("Expand and collapse from a button", commands,
            note="expand_all() and collapse_all() return a client command "
                 "for any on_click — no round-trip.")
