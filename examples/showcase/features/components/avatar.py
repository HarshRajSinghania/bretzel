"""``/avatar`` — a face, or the initials that stand in for it."""

from bretzel import ui
from bretzel.state import ClientState, field
from examples.showcase.lib.example import example, page_header

SUMMARY = ("A photo when there is one, initials when there is not, and a "
           "presence dot — six sizes, two shapes.")


def photos_and_initials() -> None:
    with ui.hstack(gap="md", wrap=True, justify="center"):
        ui.avatar(src="https://i.pravatar.cc/96?u=ada", name="Ada Lovelace")
        ui.avatar(src="https://i.pravatar.cc/96?u=grace", name="Grace Hopper")
        ui.avatar(name="Alan Turing")
        ui.avatar(name="Katherine Johnson", color="secondary")
        ui.avatar(initials="MH", color="success")


def sizes() -> None:
    with ui.hstack(gap="md", wrap=True, justify="center", align="end"):
        for size in ("xs", "sm", "md", "lg", "xl", "2xl"):
            ui.avatar(src="https://i.pravatar.cc/96?u=linus", name="Linus Ek",
                      size=size)


def presence() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center"):
        for name, status in (("Ada Lovelace", "online"),
                             ("Grace Hopper", "away"),
                             ("Alan Turing", "busy"),
                             ("Edsger Dijkstra", "offline")):
            with ui.vstack(gap="xs", align="center"):
                ui.avatar(src=f"https://i.pravatar.cc/96?u={name}", name=name,
                          size="lg", status=status)
                ui.text(status.capitalize(), size="sm", color="muted")


def workspaces() -> None:
    with ui.hstack(gap="md", wrap=True, justify="center"):
        ui.avatar(name="Northwind Traders", shape="square", color="primary")
        ui.avatar(name="Lumen Studio", shape="square", color="secondary")
        ui.avatar(name="Atlas Freight", shape="square", color="success")
        ui.avatar(name="Kinfolk", shape="square", color="warning")
        ui.avatar(name="Orbit Labs", shape="square", color="info")
        ui.avatar(name="Archive", shape="square", color="muted")


def team_list() -> None:
    with ui.card(padding="md", classes="w-full max-w-md"), ui.vstack(gap="md"):
        ui.heading("Design team", level=3, size="md")
        for name, role in (("Ada Lovelace", "Lead designer"),
                           ("Grace Hopper", "Product designer"),
                           ("Alan Turing", "Researcher")):
            with ui.hstack(gap="sm", justify="between"):
                with ui.hstack(gap="sm"):
                    ui.avatar(src=f"https://i.pravatar.cc/96?u={name}",
                              name=name, size="sm")
                    with ui.vstack(gap="none"):
                        ui.text(name, weight="medium")
                        ui.text(role, color="muted", size="sm")
                ui.button("Message", size="xs", variant="outline")


class Presence(ClientState):
    status: str = field(default="online")


def set_status() -> None:
    me = Presence()
    with ui.vstack(gap="md", align="center"):
        with ui.hstack(gap="sm"):
            ui.avatar(src="https://i.pravatar.cc/96?u=you", name="Jean Martin",
                      size="xl", status=me.status)
            with ui.vstack(gap="none"):
                ui.text("Jean Martin", weight="medium")
                ui.text("Customer success", color="muted", size="sm")
        ui.toggle_group(value=me.status, size="sm",
                        options=[("online", "Online"), ("away", "Away"),
                                 ("busy", "Busy"), ("offline", "Offline")])


def page() -> None:
    page_header("avatar", "Avatar", SUMMARY)
    example("Photos and initials", photos_and_initials,
            note="Without src, the initials come from name=; the tint is "
                 "yours to pick.")
    example("Sizes", sizes)
    example("Presence", presence,
            note="status= adds the dot: online, away, busy or offline.")
    example("Square, for things that are not people", workspaces,
            note="Workspaces, companies, projects — the square shape tells "
                 "them apart from a person.")
    example("In a team list", team_list)
    example("Set your status", set_status, uses=[Presence],
            note="status is bindable: tied to a ClientState, the dot follows "
                 "the toggle in the browser, without a request.")
