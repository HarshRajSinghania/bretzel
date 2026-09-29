"""``/iframe`` — another document inside the page, sandboxed by default."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("Embed a map, a preview or a third-party page — with a required "
           "title, a reserved ratio and a safe sandbox by default.")

MAP = ("https://www.openstreetmap.org/export/embed.html"
       "?bbox=2.3300%2C48.8580%2C2.3500%2C48.8660&layer=mapnik"
       "&marker=48.8620%2C2.3400")


def office_map() -> None:
    with ui.grid(cols={"base": 1, "md": 3}, gap="lg", classes="w-full"):
        with ui.vstack(gap="xs"):
            ui.heading("Visit us", level=3, size="lg")
            ui.text("12 rue du Louvre, 75001 Paris", size="sm")
            ui.text("Monday to Friday, 9:00 – 18:00", size="sm", color="muted")
        ui.iframe(MAP, title="Map of the Paris office", ratio="video",
                  classes="md:col-span-2")


EMAIL = """<body style="font-family:system-ui;margin:0;padding:24px;background:#fff;color:#222">
<h2 style="margin:0 0 8px">Your invoice is ready</h2>
<p>Hi Maya, invoice <b>INV-2041</b> for <b>€4,280.00</b> is attached.</p>
<p style="margin:24px 0"><a href="#" style="background:#4f46e5;color:#fff;
padding:10px 18px;border-radius:6px;text-decoration:none">View invoice</a></p>
<p style="color:#777;font-size:13px">Northwind Traders · Billing</p>
</body>"""


def email_preview() -> None:
    with ui.card(padding="md", classes="w-full max-w-2xl"), ui.vstack(gap="sm"):
        with ui.hstack(justify="between"):
            ui.text("Template: invoice-ready", weight="medium")
            ui.badge("Sandboxed", icon_left="shield-check", color="success",
                     variant="soft", size="sm")
        ui.iframe(title="Email preview", ratio="wide", sandbox="",
                  attrs={"srcdoc": EMAIL})


LANDING = """<body style="font-family:system-ui;margin:0;text-align:center;
background:#fff;font-size:13px">
<div style="padding:36px 16px;background:#0f766e;color:#fff">
<h1 style="margin:0 0 8px;font-size:20px">Fresh bread, every morning</h1>
<p style="margin:0">Order before 22:00, pick up from 7:00.</p></div>
<p style="padding:16px;color:#444">Sourdough · Baguette · Croissants</p>
<p style="margin:0 16px;padding:10px;border-radius:6px;background:#0f766e;
color:#fff">Order now</p>
</body>"""


def mobile_preview() -> None:
    with ui.hstack(gap="lg", align="center", wrap=True, justify="center"):
        with ui.vstack(gap="xs", classes="max-w-xs"):
            ui.heading("Mobile preview", level=3, size="lg")
            ui.text("See the landing page exactly as a phone renders it, "
                    "before you publish.", color="muted", size="sm")
        with ui.vstack(classes="w-72 shrink-0"), ui.card(padding="xs"):
            ui.iframe(title="Landing page on a phone", ratio="portrait",
                      attrs={"srcdoc": LANDING})


def page() -> None:
    page_header("iframe", "Iframe", SUMMARY)
    example("A map on the contact page", office_map, full=True,
            note="title= is required: it is what a screen reader announces "
                 "for the frame.")
    example("An email preview, fully locked", email_preview,
            note="sandbox=\"\" refuses everything — scripts, forms, popups. "
                 "The right setting for HTML you did not write.")
    example("A mobile preview", mobile_preview,
            note="The default sandbox allows scripts, forms and popups; the "
                 "portrait ratio frames it like a phone.")
