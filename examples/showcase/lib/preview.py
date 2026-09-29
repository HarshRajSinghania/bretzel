"""A realistic screen, built from real components — the theme's test card.

A theme is judged on a screen, not on swatches: the same page shows
whether the accent survives next to a chart, whether a badge reads on a
table row, whether the corners of a card and of its fields agree. The
home page and the studio both render it.
"""

from bretzel import ui

WEEKLY = [("Mon", 42), ("Tue", 58), ("Wed", 51), ("Thu", 73), ("Fri", 66),
          ("Sat", 38), ("Sun", 29)]

ORDERS = [
    {"id": "INV-2041", "customer": "Northwind Traders", "amount": "€4,280.00",
     "status": "paid"},
    {"id": "INV-2040", "customer": "Lumen Studio", "amount": "€1,150.00",
     "status": "pending"},
    {"id": "INV-2039", "customer": "Atlas Freight", "amount": "€9,600.00",
     "status": "overdue"},
    {"id": "INV-2038", "customer": "Kinfolk & Co", "amount": "€720.00",
     "status": "paid"},
]

STATUS = {"paid": ("Paid", "success"), "pending": ("Pending", "warning"),
          "overdue": ("Overdue", "error")}


def status_cell(value, _row):
    label, color = STATUS[value]
    return ui.badge(label, color=color, variant="soft", size="sm")


def customer_cell(value, _row):
    with ui.hstack(gap="sm") as cell:
        ui.avatar(name=value, size="xs", color="secondary")
        ui.text(value, weight="medium")
    return cell


COLUMNS = [
    ui.column("id", label="Invoice"),
    ui.column("customer", label="Customer", render=customer_cell),
    ui.column("status", label="Status", render=status_cell),
    ui.column("amount", label="Amount", align="right"),
]


def stat_card(label: str, value: str, delta: str, trend: list[int], color: str) -> None:
    with ui.card(padding="md"), ui.vstack(gap="xs"):
        ui.text(label, size="sm", color="muted")
        with ui.hstack(gap="sm", justify="between", align="end"):
            ui.heading(value, level=3, size="2xl")
            ui.sparkline(data=trend, color=color, area_fill=True, size="sm")
        ui.badge(delta, color=color, variant="soft", size="sm")


def sample_screen() -> None:
    """An invoicing dashboard: header, KPIs, a chart, a form, a table."""
    with ui.vstack(gap="md", classes="w-full"):
        with ui.hstack(gap="md", justify="between", wrap=True):
            with ui.vstack(gap="none"):
                ui.heading("Revenue", level=2, size="xl")
                ui.text("Last 30 days, all workspaces", color="muted", size="sm")
            with ui.hstack(gap="sm"):
                ui.button("Export", icon_left="download", variant="outline")
                ui.button("New invoice", icon_left="plus")
        with ui.grid(min_col="12rem", gap="md"):
            stat_card("Revenue", "€48.2k", "+12.4% vs last month",
                      [18, 22, 19, 27, 31, 29, 36], "primary")
            stat_card("Paid invoices", "184", "+8 this week",
                      [12, 14, 13, 17, 16, 19, 21], "success")
            stat_card("Overdue", "€9.6k", "3 invoices late",
                      [4, 3, 5, 4, 6, 7, 6], "error")
        with ui.grid(min_col="20rem", gap="md"):
            with ui.card(padding="md"), ui.vstack(gap="sm"):
                with ui.hstack(justify="between"):
                    ui.heading("Weekly sales", level=3, size="md")
                    ui.badge("Live", color="info", variant="soft", size="sm",
                             icon_left="radio")
                ui.bar_chart(data=WEEKLY, color="primary", size="sm")
            with ui.card(padding="md"), ui.vstack(gap="sm"):
                ui.heading("Invite a teammate", level=3, size="md")
                with ui.form_field(label="Email"):
                    ui.input(placeholder="ada@company.com", type="email",
                             icon_left="mail")
                with ui.form_field(label="Role"):
                    ui.select(options=["Viewer", "Editor", "Admin"],
                              value="Editor")
                ui.switch(label="Can approve invoices", checked=True)
                ui.button("Send invitation", classes="self-start")
        # No card around it: a table draws its own frame, and two 1 px
        # borders side by side read as one of 2 px.
        ui.table(columns=COLUMNS, rows=ORDERS, row_key="id")
        ui.alert("Two invoices are due tomorrow. Reminders go out at 9:00.",
                 title="Heads up", color="warning", icon="bell")
