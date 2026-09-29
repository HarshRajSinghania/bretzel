"""The docs' error pages — a feature like any other.

``@error_page`` is a free decorator; ``main`` picks these marks up
through ``app.include(errors)``.
"""

from bretzel import error_page, ui



@error_page(404)
def not_found() -> None:
    with ui.vstack(gap="md", align="center", justify="center",
                   classes="min-h-screen"):
        ui.heading("404", level=1, size="4xl", color="muted")
        ui.text("This page does not exist.", color="muted")
        ui.link("Back to the home page", href="/")


@error_page(500)
def server_error() -> None:
    with ui.vstack(gap="md", align="center", justify="center",
                   classes="min-h-screen"):
        ui.heading("500", level=1, size="4xl", color="error")
        ui.text("Something broke on the server.", color="muted")
        ui.link("Back to the home page", href="/")
