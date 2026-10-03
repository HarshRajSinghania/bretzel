"""TOPIC — The two scrolling models.

Bretzel does BOTH, and it is deliberate:

- **the document scrolls** — the web's model, a site's. It is the
  default: one writes nothing in particular;
- **the document is FROZEN**, and regions scroll — a tool's model. A
  sidebar that does not move, a header always there, a list scrolling on
  its own.

The repository already did both without saying so — 8 apps against 10 —
and ``ui.viewport`` / ``ui.pane`` arrived to name the second.
"""

from __future__ import annotations

from bretzel import page, ui
from examples.docs.features.shell import shell

PATH = "/scrolling"


@page(PATH, layout=shell, title="Scrolling · Bretzel docs",
      description="Scrolling in Bretzel: a document that scrolls whole, or an app shell whose sidebar and header stay while the content moves.")
def scrolling_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading('Scrolling', level=1, size="3xl")
            ui.text(
                'A site page scrolls whole. A tool does not: its sidebar '
                'stays, its header stays, and it is the central area that '
                'moves. Bretzel does both, and the choice is made once, at'
                ' the shell.',
                color="muted", size="lg",
            )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('The default: the document scrolls', level=2)
                    ui.text(
                        'Nothing to write. A page grows, the browser '
                        'scrolls. It is the model of most sites, and of '
                        "the majority of the repository's examples.",
                        color="muted", size="sm",
                    )
                    ui.code(
                        "@layout\n"
                        "def coque() -> None:\n"
                        "    with ui.vstack(gap=\"md\", classes=\"p-8\"):\n"
                        "        ui.heading(\"Mon app\")\n"
                        "        ui.outlet()\n",
                        lang="python",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('The other: the document is frozen', level=2)
                    ui.text(
                        '`ui.viewport` is a full-screen frame, out of the '
                        'flow: IT does not scroll. `ui.pane` is a region '
                        'that takes the remaining space and scrolls on its'
                        " own. That is exactly what this documentation's "
                        'shell does.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        '@layout\ndef shell() -> None:\n    with ui.viewport():          # does NOT scroll\n        with ui.sidebar(collapsible="rail"):\n            ...                  # stays in place\n        with ui.pane(padding="lg"):\n            ui.outlet()          # scrolls, on its own\n',
                        lang="python",
                    )
                    ui.text(
                        '`ui.viewport` is a `Flex`: it accepts '
                        '`direction`, `gap`, `align`, `justify`. By '
                        'default its children are in a row — sidebar on '
                        'the left, panel on the right.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading("Which one to pick", level=2)
                    ui.table(
                        columns=[
                            ui.column("si", label="If"),
                            ui.column("alors", label="Then"),
                        ],
                        rows=[
                            {"si": 'a content page one reads top to bottom',
                             "alors": 'the default — the document scrolls'},
                            {"si": 'a sidebar or a header that must stay '
                                   'visible',
                             "alors": "`ui.viewport` + `ui.pane`"},
                            {"si": 'two lists side by side that scroll '
                                   'independently',
                             "alors": "`ui.viewport` + two `ui.pane`"},
                            {"si": 'one hesitates',
                             "alors": 'the default. Freezing the document '
                                      'is a commitment: everything that '
                                      'overflows must live in a region'},
                        ],
                        size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('What freezing the document implies',
                               level=2)
                    ui.alert(
                        'Everything that overflows must be INSIDE a '
                        'scrolling region. Content placed directly in the '
                        '`ui.viewport` is cut off, with no scrollbar to '
                        'catch it — the frame does not scroll, that is its'
                        ' definition.',
                        color="warning", title='The main trap',
                    )
                    ui.alert(
                        '`document.body.scrollHeight` is 0 in this model, '
                        'and `window.scrollTo` does nothing: it is not the'
                        ' document that carries the scrolling. A script — '
                        'or a test — that wants to scroll must target the '
                        'region. Measured while writing this '
                        "documentation's probes, where the instrument "
                        'first returned 0 px of total height.',
                        color="info",
                        title='What surprises you when scripting',
                    )

            with ui.card(color="surface"):
                with ui.vstack(gap="sm"):
                    ui.heading('This page is an example of it', level=2)
                    ui.text(
                        'The left bar does not move when this text scrolls'
                        ' — it is a `ui.viewport` with a `ui.sidebar` and '
                        'a `ui.pane`. The playground too. The simpler '
                        'demonstration apps, for their part, let the '
                        'document scroll.',
                        color="muted", size="sm",
                    )
