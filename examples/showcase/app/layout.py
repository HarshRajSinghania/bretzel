"""The shell: the catalogue on the left, the theme bar above the page.

The shell is where the whole app gets its paint: ``ui.viewport`` carries
:func:`repaint_effect`, which reads the ``Studio`` store. An identity
picked here, or a knob moved in ``/studio``, repaints every page.
"""

from bretzel import Screen, ui
from bretzel.theme import ColorScheme
from examples.showcase.app.catalog import CATALOG
from examples.showcase.lib.identities import IDENTITIES
from examples.showcase.lib.studio import Studio, repaint_effect

GITHUB = "https://github.com/JeanHoccart/bretzel"
DOCS = "https://docs.bretzel-py.dev"


def identity_menu() -> None:
    with ui.dropdown(
        trigger=ui.button("Theme", icon_left="palette", icon_right="chevron-down",
                          variant="outline", size="sm"),
        align="end",
    ):
        for identity in IDENTITIES:
            ui.dropdown_item(label=identity.name, on_click=identity.apply())
        ui.dropdown_item(label="Open the studio", icon_left="sliders-horizontal",
                         href="/studio")


def theme_bar(sidebar: ui.sidebar | None) -> None:
    with ui.hstack(gap="sm", justify="end", classes="w-full"):
        if sidebar is not None:
            # On a phone the sidebar leaves the flow (``overlay``): this
            # trigger is the way back to it.
            ui.sidebar_trigger(sidebar, icon="menu")
            ui.text("Bretzel UI", weight="semibold", classes="me-auto")
        identity_menu()
        ui.icon_button("sun-moon", variant="ghost", size="sm",
                       on_click=ColorScheme.toggle(), tooltip="Light / dark")
        ui.icon_button("github", variant="ghost", size="sm", href=GITHUB,
                       external=True, tooltip="Source on GitHub")


def shell() -> None:
    ui.meta_tag(name="robots", content="index,follow,max-image-preview:large")
    ui.meta_tag(property="og:type", content="website")
    ui.meta_tag(property="og:site_name", content="Bretzel UI")
    ui.meta_tag(property="og:description",
                content="Every Bretzel component in real uses, with its Python "
                        "code, under a theme you can switch and tune live.")
    ui.meta_tag(name="twitter:card", content="summary")
    Studio()
    mobile = Screen().is_mobile
    with ui.viewport(attrs={"bz-effect": repaint_effect()}):
        # Desktop: a rail. Phone: an overlay that slides in over the page —
        # a rail would eat a fifth of a 390 px screen for good.
        sidebar = ui.sidebar(collapsible="overlay" if mobile else "rail",
                             open=not mobile)
        with sidebar:
            ui.sidebar_title("Bretzel UI", icon=ui.icon("shapes", color="primary", size="lg"),
                             href="/")
            with ui.sidebar_section():
                ui.sidebar_item("Overview", icon="house", href="/")
                ui.sidebar_item("Theme studio", icon="palette", href="/studio")
            for group, entries in CATALOG:
                with ui.sidebar_section(label=group):
                    for slug, label, icon in entries:
                        ui.sidebar_item(label, icon=icon, href=f"/{slug}")
            with ui.sidebar_footer(name="Bretzel", subtitle="Documentation & source"):
                ui.sidebar_footer_item(label="Documentation", icon_left="book-open",
                                       href=DOCS)
                ui.sidebar_footer_item(label="GitHub", icon_left="github", href=GITHUB)
        with ui.pane(gap="lg", padding="lg", classes="max-md:p-4"):
            theme_bar(sidebar if mobile else None)
            # The outlet is the page's own column: its sections are its
            # children, so the rhythm between them is set here, once.
            ui.outlet(classes="flex flex-col gap-14 w-full max-w-5xl mx-auto pb-16")
