"""How Bretzel compares — the positioning page.

What a reader comparing Python UI frameworks needs: where each one keeps
the interface's state, how the browser follows, what has to be built,
what ships in the box — and when the OTHER framework is the better pick.

Every statement about another project comes from its own documentation,
listed at the bottom with the date it was read. No benchmark, no
adjective: a choice and its trade-off. When one of those projects changes,
this page is wrong until someone re-reads the sources — hence the date.
"""

from bretzel import page, ui

from examples.docs.features.shell import shell

CHECKED_ON = "3 October 2026"

# (framework, where the interface lives, browser <-> server,
#  JavaScript build, components in the box)
GRID: tuple[tuple[str, str, str, str, str], ...] = (
    ("Bretzel",
     "Typed state classes on the server; the regions that read a state are "
     "re-rendered as HTML when it changes",
     "Plain HTTP for actions; a one-way SSE stream pushes changes to other "
     "windows; HTMX + idiomorph swap the fragments",
     "None for the app author (Tailwind v4 is compiled by a standalone "
     "binary)",
     "100+ ui.* components, charts included"),
    ("NiceGUI",
     "A tree of UI element objects kept on the server for each client",
     "WebSocket",
     "None for the user; Vue and Quasar run in the browser",
     "Yes, Quasar-based"),
    ("Reflex",
     "State classes on the server; the frontend is compiled to a Next.js "
     "(React) single-page app",
     "WebSocket, one client token per tab",
     "Yes: Reflex compiles and builds the Next.js frontend for you",
     "50+, many based on Radix UI; React components can be wrapped"),
    ("FastHTML",
     "Python functions returning HTML (FT components); state is yours to "
     "organise",
     "HTTP with HTMX; WebSockets available",
     "None",
     "None built in"),
    ("Streamlit",
     "The script reruns from top to bottom on each interaction; "
     "st.session_state keeps values between reruns",
     "WebSocket, one session per tab",
     "None",
     "Yes, widgets"),
)

# (framework, choose it when…, choose Bretzel when…)
CHOICES: tuple[tuple[str, str, str], ...] = (
    ("NiceGUI",
     "you want a proven toolkit with a large community and component set, "
     "and you like manipulating UI element objects directly.",
     "you would rather declare typed state and let the regions that read it "
     "re-render, keep a plain-HTTP application with a one-way stream for "
     "pushed updates, and have several windows follow the same change."),
    ("Reflex",
     "you want the React ecosystem: wrapping existing React components and "
     "a frontend that runs as a client-side app.",
     "you would rather not build or operate a Next.js frontend, and want the "
     "server to render HTML fragments directly from your Python state."),
    ("FastHTML",
     "you want to stay close to HTML and HTMX, with little abstraction, and "
     "assemble your own pieces.",
     "you want the application model on top: state scopes (page, session, "
     "user, app), dependency-driven regions, multi-window broadcast, forms, "
     "authentication doors and integrated components."),
    ("Streamlit",
     "rerunning a script is the right mental model — data exploration, "
     "quick dashboards — and you value its very large ecosystem.",
     "the app outgrows reruns: explicit state lifetimes, targeted updates "
     "instead of a full rerun, navigation, several users on the same data, "
     "and interactions the server arbitrates."),
)

NOT_YET: tuple[str, ...] = (
    "It is an alpha: APIs can change between alpha releases, and only the "
    "latest alpha receives fixes.",
    "It has one maintainer and a young community — fewer answers already "
    "written on the web than for the projects above.",
    "No ORM: bring SQLAlchemy, Tortoise or asyncpg.",
    "No WebSocket: actions are HTTP requests and pushed updates use SSE.",
    "Python 3.12 or newer.",
)

SOURCES: tuple[tuple[str, str], ...] = (
    ("NiceGUI — configuration & deployment",
     "https://nicegui.io/documentation/section_configuration_deployment"),
    ("Reflex — introduction", "https://reflex.dev/docs/getting-started/introduction/"),
    ("Reflex — architecture", "https://reflex.dev/blog/2024-03-21-reflex-architecture/"),
    ("FastHTML — documentation", "https://www.fastht.ml/docs/"),
    ("Streamlit — client-server architecture",
     "https://docs.streamlit.io/develop/concepts/architecture/architecture"),
    ("Streamlit — Session State",
     "https://docs.streamlit.io/develop/concepts/architecture/session-state"),
)


@page("/compare", layout=shell,
      title="Bretzel compared — NiceGUI, Reflex, FastHTML, Streamlit · Bretzel docs",
      description="How Bretzel, a server-driven Python web framework, compares with NiceGUI, Reflex, FastHTML and Streamlit: where state lives, transport, build step, components, and when to pick each.")
def compare_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading("How Bretzel compares", level=1, size="3xl")
            ui.text(
                "Several Python frameworks build web interfaces without a "
                "separate JavaScript application. They differ on one "
                "question above all: where the interface's state lives, and "
                "how the browser follows it. This page states each choice, "
                "taken from each project's own documentation, so you can "
                "pick the one that fits. Bretzel is the youngest of them.",
                color="muted", size="lg",
            )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading("At a glance", level=2)
                    ui.table(
                        columns=[
                            ui.column("name", label="Framework"),
                            ui.column("model", label="Where the interface lives"),
                            ui.column("wire", label="Browser ↔ server"),
                            ui.column("build", label="JavaScript build"),
                            ui.column("parts", label="Components in the box"),
                        ],
                        rows=[
                            {"name": n, "model": m, "wire": w,
                             "build": b, "parts": p}
                            for n, m, w, b, p in GRID
                        ],
                        size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="md"):
                    ui.heading("Which one, when", level=2)
                    for name, theirs, ours in CHOICES:
                        with ui.vstack(gap="xs"):
                            ui.heading(f"Bretzel or {name}", level=3)
                            with ui.hstack(align="baseline", gap="sm"):
                                ui.icon("arrow-right", color="muted", size="sm")
                                ui.text(f"Choose {name} when {theirs}", size="sm")
                            with ui.hstack(align="baseline", gap="sm"):
                                ui.icon("arrow-right", color="primary", size="sm")
                                ui.text(f"Choose Bretzel when {ours}", size="sm")

            with ui.card(color="warning"):
                with ui.vstack(gap="sm"):
                    ui.heading("Where Bretzel is not the right pick today",
                               level=2)
                    with ui.vstack(gap="xs"):
                        for line in NOT_YET:
                            with ui.hstack(align="baseline", gap="sm"):
                                ui.icon("info", color="warning", size="sm")
                                ui.text(line, size="sm")

            with ui.card(color="surface"):
                with ui.vstack(gap="sm"):
                    ui.heading("See it for yourself", level=2)
                    ui.text(
                        "Open the live Kanban in two windows of the same "
                        "browser: drag a card in one, the other follows — one "
                        "Python app, no JavaScript written.",
                        size="sm",
                    )
                    with ui.hstack(gap="sm", wrap=True):
                        ui.button("Open the live Kanban",
                                  href="https://demo.bretzel-py.dev",
                                  icon_right="arrow-up-right")
                        ui.button("Start in 5 minutes", href="/quickstart",
                                  variant="outline", icon_right="arrow-right")

            with ui.vstack(gap="xs"):
                ui.text(f"Sources, read on {CHECKED_ON}:", size="sm",
                        color="muted")
                for label, url in SOURCES:
                    ui.link(label, href=url, external=True)
                ui.text(
                    "Something wrong or out of date about another project? "
                    "Open an issue on GitHub and it will be corrected.",
                    size="sm", color="muted",
                )
