"""``/html`` — trusted markup, injected as is."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("The escape hatch for markup no component covers — inline SVG, "
           "native elements — written as a literal you trust.")


def logo() -> None:
    with ui.hstack(gap="sm"):
        ui.html('<svg width="40" height="40" viewBox="0 0 40 40" fill="none" '
                'stroke="currentColor" stroke-width="3" stroke-linecap="round" '
                'aria-hidden="true"><path d="M8 28c0-10 6-18 12-18s12 8 12 18"/>'
                '<path d="M14 28c0-6 3-11 6-11s6 5 6 11"/>'
                '<circle cx="20" cy="30" r="3" fill="currentColor"/></svg>',
                classes="text-primary")
        with ui.vstack(gap="none"):
            ui.text("Northwind", weight="bold", size="lg")
            ui.text("Billing, done.", size="sm", color="muted")


def shortcuts() -> None:
    with ui.card(padding="md", classes="w-full max-w-sm"), ui.vstack(gap="sm"):
        ui.heading("Keyboard shortcuts", level=3, size="md")
        ui.html('<dl class="grid grid-cols-[1fr_auto] gap-y-2 text-sm">'
                '<dt>Search everything</dt><dd><kbd class="rounded border '
                'border-text/20 bg-surface px-1.5 font-mono text-xs">Ctrl</kbd> '
                '<kbd class="rounded border border-text/20 bg-surface px-1.5 '
                'font-mono text-xs">K</kbd></dd>'
                '<dt>New invoice</dt><dd><kbd class="rounded border '
                'border-text/20 bg-surface px-1.5 font-mono text-xs">N</kbd></dd>'
                '<dt>Close panel</dt><dd><kbd class="rounded border '
                'border-text/20 bg-surface px-1.5 font-mono text-xs">Esc</kbd></dd>'
                '</dl>', classes="w-full")


def faq() -> None:
    ui.html('<details class="group rounded-box border border-text/10 p-4" open>'
            '<summary class="cursor-pointer font-medium">Can I change plans '
            'at any time?</summary><p class="mt-2 text-sm text-text/70">Yes. '
            'Upgrades apply immediately; downgrades at the end of the '
            'billing period.</p></details>'
            '<details class="mt-3 rounded-box border border-text/10 p-4">'
            '<summary class="cursor-pointer font-medium">Do you offer '
            'refunds?</summary><p class="mt-2 text-sm text-text/70">Within '
            '30 days of any payment, no questions asked.</p></details>',
            classes="w-full max-w-lg")


def storage_meter() -> None:
    with ui.vstack(gap="xs", classes="w-full max-w-sm"):
        with ui.hstack(justify="between"):
            ui.text("Storage", size="sm", weight="medium")
            ui.text("7.2 GB of 10 GB", size="sm", color="muted")
        ui.html('<meter min="0" max="10" low="7" high="9" optimum="2" value="7.2" '
                'class="w-full h-3">7.2 GB</meter>', classes="w-full")


def page() -> None:
    page_header("html", "HTML", SUMMARY)
    example("An inline SVG logo", logo,
            note="The SVG draws in currentColor, so it takes the theme's colour.")
    example("Keyboard shortcuts", shortcuts,
            note="Native <kbd> and <dl> elements, with Tailwind classes that "
                 "read the theme's tokens.")
    example("A native disclosure", faq,
            note="<details> opens and closes with no JavaScript at all.")
    example("A native meter", storage_meter,
            note="Only for markup you wrote: ui.html does not escape anything. "
                 "User text goes to ui.text or ui.markdown.")
