"""``/badge`` — a status, a count, a tag."""

import functools

from bretzel import refreshable, ui
from bretzel.state import PageState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Status pills, counters and removable filter chips — three "
           "variants, every colour, five sizes.")


def variants() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        ui.badge("Solid", variant="solid", size="lg")
        ui.badge("Soft", variant="soft", size="lg")
        ui.badge("Outline", variant="outline", size="lg")


def colors() -> None:
    with ui.vstack(gap="sm", align="center"):
        for variant in ("solid", "soft", "outline"):
            with ui.hstack(gap="sm", wrap=True, justify="center"):
                for color in ("primary", "secondary", "success", "warning",
                              "error", "info", "muted"):
                    ui.badge(color.capitalize(), color=color, variant=variant)


def sizes() -> None:
    with ui.hstack(gap="sm", wrap=True, justify="center", align="center"):
        for size in ("xs", "sm", "md", "lg", "xl"):
            ui.badge(f"Size {size}", size=size, variant="soft")


def in_a_list() -> None:
    invoices = [
        ("INV-2041", "Northwind Traders", "Paid", "success", "check"),
        ("INV-2040", "Lumen Studio", "Pending", "warning", "clock"),
        ("INV-2039", "Atlas Freight", "Overdue", "error", "circle-alert"),
        ("INV-2038", "Kinfolk & Co", "Draft", "muted", "pencil"),
    ]
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="sm"):
        for number, customer, status, color, icon in invoices:
            with ui.hstack(gap="md", justify="between"):
                with ui.vstack(gap="none"):
                    ui.text(customer, weight="medium")
                    ui.text(number, color="muted", size="sm")
                ui.badge(status, color=color, variant="soft", size="sm",
                         icon_left=icon)


def counters() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center"):
        with ui.hstack(gap="xs"):
            ui.text("Inbox", weight="medium")
            ui.badge("12", color="primary", size="xs")
        with ui.hstack(gap="xs"):
            ui.text("Mentions", weight="medium")
            ui.badge("3", color="error", size="xs")
        with ui.hstack(gap="xs"):
            ui.text("Plan", weight="medium")
            ui.badge("Pro", color="secondary", variant="outline", size="xs",
                     icon_left="sparkles")
        with ui.hstack(gap="xs"):
            ui.text("API", weight="medium")
            ui.badge("Beta", color="info", variant="soft", size="xs",
                     icon_right="flask-conical")


def default_filters() -> list[str]:
    return ["Status: Open", "Owner: Ada", "Label: Billing", "Due this week"]


class Filters(PageState):
    active: list[str] = field(default_factory=default_filters)


def remove_filter(label: str) -> None:
    filters = Filters()
    filters.active = [f for f in filters.active if f != label]


def reset_filters() -> None:
    Filters().active = default_filters()


@refreshable(deps=[Filters])
def filter_chips() -> None:
    active = Filters().active
    with ui.hstack(gap="sm", wrap=True, justify="center"):
        for label in active:
            ui.badge(label, variant="soft", color="primary", dismissible=True,
                     on_close=functools.partial(remove_filter, label))
        if not active:
            ui.text("No filters — showing all 248 tickets.", color="muted",
                    size="sm")
        ui.button("Reset", size="xs", variant="ghost", icon_left="rotate-ccw",
                  on_click=reset_filters)


def filter_bar() -> None:
    filter_chips()


def page() -> None:
    page_header("badge", "Badge", SUMMARY)
    example("Variants", variants)
    example("Colours", colors,
            note="Every semantic colour of the theme, in each variant.")
    example("Sizes", sizes)
    example("Status in a list", in_a_list,
            note="Soft badges with an icon read at a glance without shouting "
                 "over the row.")
    example("Counters and tags", counters)
    example("Removable filters", filter_bar,
            uses=[default_filters, Filters, remove_filter, reset_filters, filter_chips],
            note="dismissible adds the ×; on_close runs Python with the chip "
                 "it came from, and the zone re-renders.")
