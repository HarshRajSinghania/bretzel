"""REACTIVITY — Client reactivity.

The client side of reactivity: when a client state changes, the browser
updates the display on its own, with no round trip. Reading a
ClientState field in a render gives a ClientBinding; passing it to a
reactive prop (`bz-text`, `bz-show`, `visible=`) wires the live update.
The operators compose a ClientExpression.
"""

from __future__ import annotations

from bretzel import page, ui
from bretzel.state import ClientState, field
from examples.docs.features.shell import shell
from examples.docs.lib.blocks import client_algebra_mirror

PATH = "/reactivity-client"


class PanelUI(ClientState, persist="memory"):
    open: bool = field(default=False)


class NumberUI(ClientState, persist="memory"):
    n: int = field(default=0)


def toggle_demo() -> None:
    panel = PanelUI()
    with ui.vstack(gap="sm"):
        ui.button("Show / hide", on_click=panel.open.toggle())
        with ui.card(color="primary", visible=panel.open):
            ui.text('I show myself through `visible=binding` — bz-show, '
                    'zero round trips.')


def number_demo() -> None:
    num = NumberUI()
    with ui.hstack(align="center", gap="md"):
        ui.button("−", variant="outline", on_click=num.n.decrement())
        ui.text(num.n, weight="bold", classes="font-mono w-8 text-center")
        ui.button("+", on_click=num.n.increment())
        ui.badge("n > 3", color="success", visible=(num.n > 3))


@page(PATH, layout=shell, title="Client reactivity · Bretzel docs",
      description="Client reactivity in Bretzel: bind a ClientState to a reactive prop and the browser updates the display itself, with no request.")
def reactivity_client_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading('Client reactivity', level=1, size="3xl")
            with ui.hstack(align="baseline", gap="sm", wrap=True):
                ui.text(
                    'When a',
                    color="muted", size="lg",
                )
                ui.link('client state', href="/state-client")
                ui.text(
                    'changes, the browser updates the display itself — '
                    'with no request. One wires that by passing a binding '
                    'to a reactive prop.',
                    color="muted", size="lg",
                )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Reading a client state = a binding', level=2)
                    ui.text(
                        'Reading a ClientState field inside a render does '
                        'not return the raw value but a `ClientBinding` — '
                        'an object the component knows how to wire.',
                        color="muted", size="sm",
                    )
                    ui.table(
                        columns=[
                            ui.column("prop", label='Passed to…'),
                            ui.column("effet", label='Cable'),
                        ],
                        rows=[
                            {"prop": "ui.text(binding)",
                             "effet": 'bz-text — the text follows the value'},
                            {"prop": "visible=binding",
                             "effet": 'bz-show — shown/hidden according to'
                                      ' the value'},
                            {"prop": "value=binding (input)",
                             "effet": 'bz-model — two-way read/write'},
                        ],
                        size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Displaying a value', level=2)
                    ui.text(
                        'A server value read inside a render is an '
                        'ordinary Python value: one displays it directly '
                        '(str, f-string). A ClientBinding is passed as is '
                        'to `ui.text()` to stay reactive; interpolating it'
                        ' into a `str()` or an f-string raises an error.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Demo — a binding drives a bz-show', level=2)
                    toggle_demo()

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Demo — a ClientExpression drives visible=',
                               level=2)
                    ui.text(
                        'The operators on a binding (`num.n > 3`) compose '
                        'a `ClientExpression`, baked into a client-side '
                        '`bz-show`. Zero round trips.',
                        color="muted", size="sm",
                    )
                    number_demo()

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('The whole binding → JS algebra', level=2)
                    ui.text(
                        'Every `ClientBinding` operator and method, read '
                        'live from the class, with the JS it really emits '
                        '(captured by running a probe). Adding an operator'
                        ' to the algebra adds it here — with no editing. '
                        'Traps: `&`/`|`/`~` (not `and`/`or`/`not`), and '
                        'parenthesise compound comparisons `(x > 0) & (y <'
                        ' 10)`.',
                        color="muted", size="sm",
                    )
                    client_algebra_mirror()
