"""``/grid`` — two dimensions, from a fixed count to auto-fill."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Columns by count, by breakpoint or by minimum width — the grid "
           "fills the rows and keeps the gutters even.")


def tile(label: str, icon: str) -> None:
    with ui.card(padding="sm"), ui.hstack(gap="sm"):
        ui.icon(icon, size="sm", color="primary")
        ui.text(label, size="sm", weight="medium")


def fixed() -> None:
    with ui.grid(cols=3, gap="md"):
        tile("Mon 6", "calendar")
        tile("Tue 7", "calendar")
        tile("Wed 8", "calendar")
        tile("Thu 9", "calendar")
        tile("Fri 10", "calendar")
        tile("Sat 11", "calendar")


def app_card(name: str, text: str, icon: str) -> None:
    with ui.card(padding="md"), ui.vstack(gap="sm", align="start"):
        ui.icon(icon, size="lg", color="primary")
        ui.text(name, weight="semibold")
        ui.text(text, size="sm", color="muted")


def auto_fill() -> None:
    with ui.grid(min_col="12rem", gap="md"):
        app_card("Slack", "Post a message when an invoice is paid.",
                 "message-square")
        app_card("GitHub", "Link pull requests to the tasks they close.",
                 "git-branch")
        app_card("Stripe", "Sync payments and refunds every hour.",
                 "credit-card")
        app_card("Google Calendar", "Show bookings next to your meetings.",
                 "calendar")
        app_card("Mailchimp", "Add new customers to your newsletter.",
                 "mail")


def responsive() -> None:
    with ui.grid(cols={"base": 1, "sm": 2, "lg": 4}, gap="md"):
        tile("Revenue · €48.2k", "trending-up")
        tile("Orders · 1,284", "shopping-cart")
        tile("Refunds · 12", "undo-2")
        tile("Visitors · 32k", "users")


def gaps() -> None:
    with ui.vstack(gap="lg", classes="w-full"):
        for gap in ("xs", "md", "xl"):
            with ui.vstack(gap="xs"):
                ui.text(f'gap="{gap}"', size="xs", color="muted",
                        classes="font-mono")
                with ui.grid(cols=4, gap=gap):
                    for quarter in ("Q1", "Q2", "Q3", "Q4"):
                        tile(quarter, "chart-column")


def dashboard() -> None:
    with ui.grid(cols={"base": 1, "md": 3}, gap="md"):
        with ui.card(padding="md", classes="md:col-span-2"), ui.vstack(gap="sm"):
            ui.text("Weekly sales", weight="semibold")
            ui.bar_chart(data=[("Mon", 42), ("Tue", 58), ("Wed", 51),
                               ("Thu", 73), ("Fri", 66)],
                         color="primary", size="sm")
        with ui.card(padding="md"), ui.vstack(gap="sm"):
            ui.text("Goals", weight="semibold")
            ui.text("Quarterly revenue", size="sm", color="muted")
            ui.progress(value=72, color="success")
            ui.text("New customers", size="sm", color="muted")
            ui.progress(value=45, color="info")
            ui.text("Support backlog", size="sm", color="muted")
            ui.progress(value=18, color="warning")


def page() -> None:
    page_header("grid", "Grid", SUMMARY)
    example("A fixed number of columns", fixed, uses=[tile], full=True,
            note="cols=3: six items fill two rows of three.")
    example("As many columns as fit", auto_fill, uses=[app_card], full=True,
            note="min_col=\"12rem\" keeps every card at least 12rem wide and "
                 "fits as many per row as the width allows.")
    example("Columns per breakpoint", responsive, uses=[tile], full=True,
            note="One column on a phone, two from sm, four from lg.")
    example("A dashboard with a wide panel", dashboard, full=True,
            note="A column span is plain Tailwind on the child.")
    example("Gutter sizes", gaps, uses=[tile], full=True)
