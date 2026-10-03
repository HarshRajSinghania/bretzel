"""REFERENCE — The ui.* catalogue.

The whole ``ui.*`` surface read live from the code. Every component is
introspected at render time (``describe_ui_symbol``): signature, bindable
props, events, slots, imperative methods — the page cannot go out of sync
with the framework.

The ``ui.*`` namespace is heterogeneous: alongside the components live
helpers (iteration ``ui.each``, toast ``ui.notification``, descriptor
``ui.column``). They have neither props nor events — listed separately.
"""

from __future__ import annotations

from bretzel import page, ui

from examples.docs.features.shell import shell
from examples.docs.lib.blocks import component_mirror, helper_mirror
from bretzel.introspect import (
    ComponentInfo,
    HelperInfo,
    describe_ui_symbol,
    ui_symbol_names,
)

PATH = "/components"

# Reading order for the families + a lucide icon each.
_FAMILY_ORDER: list[tuple[str, str, str]] = [
    ("primitives", "Primitives", "box"),
    ("layout", "Layout", "layout"),
    ("actions", "Actions", "mouse-pointer-click"),
    ("inputs", "Inputs", "keyboard"),
    ("feedback", "Feedback", "bell"),
    ("data", "Data", "table"),
    ("charts", "Charts", "trending-up"),
    ("navigation", "Navigation", "navigation"),
    ("overlay", "Overlay", "layers"),
    ("meta", "Meta", "settings"),
]


def family_card(label: str, icon: str, components: list[ComponentInfo]) -> None:
    with ui.card():
        with ui.vstack(gap="sm"):
            with ui.hstack(align="center", gap="sm"):
                ui.icon(icon, color="muted")
                ui.heading(label, level=2)
                ui.badge(str(len(components)), color="muted", variant="outline")
            with ui.accordion(multiple=True):
                for info in sorted(components, key=lambda c: c.ui_name):
                    with ui.accordion_item(info.ui_name, label=f"ui.{info.ui_name}"):
                        component_mirror(info)


@page(PATH, layout=shell, title="ui.* catalogue · Bretzel docs",
      description="The ui.* catalogue, read live from the code: every Bretzel component's signature, bindable props, events, slots and imperative methods.")
def components_page() -> None:
    infos = [describe_ui_symbol(n) for n in ui_symbol_names()]
    components = [i for i in infos if isinstance(i, ComponentInfo)]
    helpers = [i for i in infos if isinstance(i, HelperInfo)]

    by_family: dict[str, list[ComponentInfo]] = {}
    for comp in components:
        by_family.setdefault(comp.family, []).append(comp)

    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading("ui.* catalogue", level=1, size="3xl")
            ui.text(
                'The whole `ui.*` surface read live from the code — '
                'signature, bindable props, events, slots, imperative '
                'methods. This page introspects the classes at render '
                'time: it cannot fall out of step with the framework.',
                color="muted", size="lg",
            )
            ui.alert(
                "Every component in real uses, with the code that renders "
                "it, under a theme you can switch and tune.",
                title="See them rendered: the component gallery",
                icon="layout-grid",
                color="info",
            )
            ui.button("Open the component gallery", href="https://ui.bretzel-py.dev",
                      external=True, icon_right="external-link", variant="soft",
                      color="info", size="sm", classes="self-start")
            with ui.hstack(gap="sm", wrap=True):
                ui.badge(f"{len(components)} components", color="primary",
                         variant="soft")
                ui.badge(f"{len(helpers)} helpers", color="warning",
                         variant="soft")

            with ui.card(color="surface"):
                with ui.vstack(gap="xs"):
                    ui.heading("Component or helper?", level=3)
                    ui.text(
                        '`ui.*` is not homogeneous. A component renders '
                        'and carries a contract (bindable props, events, '
                        'slots, imperative methods). A helper — `ui.each` '
                        '(iteration), `ui.notification` (toast), '
                        '`ui.column` (a column descriptor) — is only a '
                        'function. Both are listed, but not mixed.',
                        color="muted", size="sm",
                    )

            for fam_key, fam_label, fam_icon in _FAMILY_ORDER:
                fam = by_family.get(fam_key)
                if fam:
                    family_card(fam_label, fam_icon, fam)

            with ui.card():
                with ui.vstack(gap="sm"):
                    with ui.hstack(align="center", gap="sm"):
                        ui.icon("wrench", color="muted")
                        ui.heading("Helpers", level=2)
                        ui.badge(str(len(helpers)), color="muted",
                                 variant="outline")
                    ui.text(
                        'These symbols live in `ui.*` but are NOT '
                        'components — no props, no events.',
                        color="muted", size="sm",
                    )
                    with ui.accordion(multiple=True):
                        for info in helpers:
                            with ui.accordion_item(info.ui_name,
                                                   label=f"ui.{info.ui_name}"):
                                helper_mirror(info)
