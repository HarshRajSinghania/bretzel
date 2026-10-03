"""Foundations — Describing the UI.

Before any interactivity: how an interface is described. Python
components composed with `with`, a page, and rendering FROM a typed
state. The complete component catalogue lives in the Reference.
"""

from bretzel import page, ui

from examples.docs.features.shell import shell


@page("/describe", layout=shell, title="Describe the UI · Bretzel docs",
      description="Describe a user interface in Python with Bretzel: ui.* components composed with with-blocks into a tree, before any state moves.")
def describe_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading('Describe the UI', level=1, size="3xl")
            ui.text(
                'Before making anything interactive, one has to know how '
                'to describe an interface. In Bretzel, a UI is a tree of '
                'Python components — static as long as no state moves.',
                color="muted", size="lg",
            )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Components composed with `with`', level=2)
                    ui.text(
                        'The `ui.*` components are functions. The '
                        'containers (stack, card, grid…) open with a '
                        '`with` block; their children are declared inside.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        'with ui.card():\n    with ui.vstack(gap="sm"):\n        ui.heading("Profile", level=2)\n        ui.text("Member since 2024", color="muted")\n        ui.button("Edit")\n',
                        lang="python",
                    )
                    with ui.hstack(align="baseline", gap="sm", wrap=True):
                        ui.text('The complete list (inputs, overlays, '
                                'tables, charts…) is in', color="muted", size="sm")
                        ui.link('the catalogue', href="/components")
                        ui.text(".", color="muted", size="sm")

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('A page', level=2)
                    ui.text(
                        'A page is a function decorated with `@page` and '
                        'its URL. A `@layout` draws the common frame (a '
                        'sidebar, a header) and exposes a region through '
                        '`ui.outlet()` where the pages render.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        "@page(\"/profile\", layout=shell)\n"
                        "def profile() -> None:\n"
                        "    ui.heading(\"Profile\", level=1)\n",
                        lang="python",
                    )

            with ui.card(color="surface"):
                with ui.vstack(gap="sm"):
                    ui.heading('Render from the state', level=2)
                    ui.text(
                        'The key point: the UI is built BY READING the '
                        'state. One never modifies the display by hand — '
                        'one describes what it must be for the current '
                        'state. When the state changes, the UI is '
                        'recomputed (that is reactivity, further on). The '
                        'flow goes one way only: state → UI.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        "def cart_summary() -> None:\n"
                        "    cart = Cart()\n"
                        "    ui.text(f\"{len(cart.items)} items\")\n"
                        "    for item in cart.items:\n"
                        "        ui.text(item[\"name\"])\n",
                        lang="python",
                    )
                    with ui.hstack(align="baseline", gap="sm", wrap=True):
                        ui.text('Where does that state come from? That is '
                                'next:',
                                color="muted", size="sm")
                        ui.link('Server state →', href="/state-server")
