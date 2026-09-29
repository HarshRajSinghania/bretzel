"""Foundations — How Bretzel works.

The boundary page: the universal client vs server concept, what each is
for, UI = f(state), and Bretzel's general cycle. Conceptual — zero
signatures. All the rest of the docs rests on this.
"""

from bretzel import page, ui

from examples.docs.features.shell import shell


_CYCLE = [
    ("mouse-pointer-click", 'An interaction happens (a click, a keystroke).'),
    ("server", 'If it changes the truth, it goes server side: a Python '
               'function runs.'),
    ("database", 'This function mutates the state.'),
    ("refresh-cw", 'The part of the interface that depends on that state '
                   'is re-rendered and sent back to the browser.'),
]


@page("/how", layout=shell, title="How Bretzel works")
def how_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading("How Bretzel works", level=1, size="3xl")
            ui.text(
                'Every web app has two halves: the browser (the client) '
                'and the server. Knowing where the code runs — and when '
                'one crosses from one to the other — is the frame that '
                'lights up everything else.',
                color="muted", size="lg",
            )

            # ── The two halves ───────────────────────────────────────
            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('The two halves', level=2)
                    ui.table(
                        columns=[
                            ui.column("cote", label='Half'),
                            ui.column("quoi", label='What it is'),
                        ],
                        rows=[
                            {"cote": "Client",
                             "quoi": "the browser, on the user's machine —"
                                     ' it displays and reacts'},
                            {"cote": "Server",
                             "quoi": 'your machine, where the Python runs '
                                     '— it holds the truth'},
                        ],
                        size="sm",
                    )

            # ── Pourquoi le serveur ──────────────────────────────────
            with ui.card(color="primary"):
                with ui.vstack(gap="sm"):
                    ui.heading('Why on the server', level=2)
                    ui.text(
                        "The web's basic rule: the client is always wrong."
                        ' Everything arriving from the browser can be '
                        'tampered with. So what matters lives server side:',
                    )
                    with ui.vstack(gap="xs"):
                        for t in [
                            'Security — the client is never trusted; the '
                            'validation that protects happens here.',
                            'Source of truth — the data is stored and '
                            'owned by the server, not by the tab.',
                            'Confidential logic — a price calculation, a '
                            'business rule must not leave for the browser.',
                            'Sharing — a server state is seen by several '
                            'users / tabs; a client state is not.',
                        ]:
                            with ui.hstack(align="baseline", gap="sm"):
                                ui.icon("check", color="primary", size="sm")
                                ui.text(t, size="sm")

            # ── Pourquoi le client ───────────────────────────────────
            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Why on the client', level=2)
                    ui.text(
                        'Going through the server costs a network request.'
                        ' For a purely visual interaction (opening a menu,'
                        ' ticking a box), it is waste. Staying client side'
                        ' means:',
                        color="muted", size="sm",
                    )
                    with ui.vstack(gap="xs"):
                        for t in [
                            'No request — it works with no round trip, '
                            'hence instantly.',
                            "Lightening the server — it is the user's "
                            'machine doing the work, not yours.',
                        ]:
                            with ui.hstack(align="baseline", gap="sm"):
                                ui.icon("check", color="success", size="sm")
                                ui.text(t, size="sm")

            # ── UI = f(state) ────────────────────────────────────────
            with ui.card(color="surface"):
                with ui.vstack(gap="xs"):
                    ui.heading("UI = f(state)", level=2)
                    ui.text(
                        'The interface is a function of the state. One '
                        'does not manipulate the DOM by hand: one '
                        'describes what the UI must be for a given state, '
                        'one mutates the state, and the UI is recomputed.',
                    )

            # ── Le cycle de Bretzel ──────────────────────────────────
            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading("Bretzel's cycle", level=2)
                    with ui.vstack(gap="sm"):
                        for i, (icon, text) in enumerate(_CYCLE, start=1):
                            with ui.hstack(align="center", gap="sm"):
                                ui.badge(str(i), color="primary", variant="soft")
                                ui.icon(icon, color="primary")
                                ui.text(text, size="sm")
                    ui.text(
                        'An interaction that does NOT change the truth '
                        '(opening a panel) short-circuits the server step '
                        'and stays in the browser.',
                        color="muted", size="sm",
                    )

            # ── An event's paths ────────────────────────────────────
            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading("An event's routes", level=2)
                    ui.text(
                        'Concretely, an event takes one of these routes:',
                        color="muted", size="sm",
                    )
                    ui.table(
                        columns=[
                            ui.column("quoi", label='The event…'),
                            ui.column("ou", label="tourne"),
                            ui.column("ar", label="Round trip?"),
                        ],
                        rows=[
                            {"quoi": 'calls a Python function',
                             "ou": "serveur", "ar": "oui"},
                            {"quoi": 'drives a component / a client state',
                             "ou": "client", "ar": "non"},
                        ],
                        size="sm",
                    )
                    ui.text(
                        'It is the same boundary, applied everywhere: '
                        'state, actions and reactivity each have a server '
                        'side and a client side. The rest of the docs '
                        'follows that plan.',
                        color="muted", size="sm",
                    )
