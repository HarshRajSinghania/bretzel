"""``/icon`` — any of the 200,000 Iconify icons, by name."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Lucide by default, any Iconify set by prefix — six sizes, every "
           "semantic colour, and a name that can change live.")


def sizes() -> None:
    with ui.hstack(gap="lg", align="end", wrap=True, justify="center"):
        for size in ("xs", "sm", "md", "lg", "xl", "2xl"):
            with ui.vstack(gap="xs", align="center"):
                ui.icon("rocket", size=size)
                ui.text(size, size="xs", color="muted", classes="font-mono")


def health_checks() -> None:
    with ui.card(padding="md", classes="w-full max-w-sm"), ui.vstack(gap="sm"):
        for icon, color, label in (("circle-check", "success", "API — operational"),
                                   ("triangle-alert", "warning", "Webhooks — delayed"),
                                   ("circle-x", "error", "Email — outage"),
                                   ("info", "info", "Search — maintenance at 22:00")):
            with ui.hstack(gap="sm"):
                ui.icon(icon, color=color)
                ui.text(label, size="sm")


def features() -> None:
    with ui.grid(min_col="12rem", gap="lg", classes="w-full"):
        for icon, title, body in (
            ("shield-check", "Single sign-on", "Google, Microsoft and any OIDC provider."),
            ("database-zap", "Instant exports", "CSV and Excel for every table, in one click."),
            ("bell-ring", "Smart reminders", "Overdue invoices chase themselves."),
        ):
            with ui.vstack(gap="sm", align="start"):
                ui.icon(icon, size="lg", color="primary")
                ui.text(title, weight="semibold")
                ui.text(body, size="sm", color="muted")


def integrations() -> None:
    with ui.grid(min_col="12rem", gap="sm", classes="w-full max-w-3xl"):
        for icon, name in (("simple-icons:slack", "Slack"),
                           ("simple-icons:stripe", "Stripe"),
                           ("simple-icons:github", "GitHub"),
                           ("simple-icons:notion", "Notion"),
                           ("simple-icons:googlecalendar", "Google Calendar"),
                           ("simple-icons:hubspot", "HubSpot")):
            with ui.card(padding="sm"), ui.hstack(gap="sm"):
                ui.icon(icon, size="md")
                ui.text(name, size="sm", weight="medium")


class Presence(ClientState):
    icon: str = field(default="circle-check")


def live_icon() -> None:
    presence = Presence()
    with ui.card(padding="md", classes="w-full max-w-md"), ui.vstack(gap="md"):
        with ui.hstack(gap="sm"):
            ui.icon(presence.icon, color="primary", size="lg")
            with ui.vstack(gap="none"):
                ui.text("Maya Chen", weight="medium")
                ui.text("Product designer", size="sm", color="muted")
        ui.toggle_group(value=presence.icon, size="sm",
                        options=[("circle-check", "Available"),
                                 ("calendar-clock", "In a meeting"),
                                 ("moon", "Away")])


def page() -> None:
    page_header("icon", "Icon", SUMMARY)
    example("Sizes", sizes,
            note="The glyph is sized in em, so an icon also follows the text around it.")
    example("Status at a glance", health_checks,
            note="color= takes a semantic colour; without it, the icon takes the "
                 "colour of its text.")
    example("A feature grid", features, full=True)
    example("Any Iconify set", integrations,
            note="Prefix the name with a set — simple-icons: for brand logos, "
                 "tabler:, ph:, mdi: and a hundred more.")
    example("An icon that follows the browser", live_icon, uses=[Presence],
            note="name= accepts a ClientState field: pick a status and the icon "
                 "swaps in the browser, with no round trip.")
