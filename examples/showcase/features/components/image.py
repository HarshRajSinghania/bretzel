"""``/image`` — a picture that keeps its place while it loads."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("An <img> with a required alt, a reserved ratio so the page never "
           "jumps, and cover or contain fitting.")


def ratios() -> None:
    with ui.grid(cols={"base": 2, "md": 4}, gap="md", classes="w-full"):
        for ratio in ("square", "portrait", "video", "wide"):
            with ui.vstack(gap="xs"):
                ui.image(f"https://picsum.photos/seed/{ratio}/640/640",
                         alt=f"Landscape photo, {ratio} crop", ratio=ratio)
                ui.text(ratio, size="xs", color="muted", classes="font-mono")


PRODUCTS = [("Linen overshirt", "€89", "linen"),
            ("Canvas tote", "€35", "tote"),
            ("Merino beanie", "€29", "beanie")]


def product_cards() -> None:
    with ui.grid(min_col="12rem", gap="md", classes="w-full max-w-3xl"):
        for name, price, seed in PRODUCTS:
            with ui.card(padding="sm", hoverable=True), ui.vstack(gap="sm"):
                ui.image(f"https://picsum.photos/seed/{seed}/480/480",
                         alt=name, ratio="square", fit="cover")
                with ui.hstack(justify="between"):
                    ui.text(name, weight="medium")
                    ui.text(price, color="muted")


def fits() -> None:
    with ui.grid(cols=2, gap="md", classes="w-full max-w-md"):
        for fit in ("cover", "contain"):
            with ui.vstack(gap="xs"):
                ui.image("https://picsum.photos/seed/harbor/800/400",
                         alt="Harbour at dawn", ratio="square", fit=fit)
                ui.text(f"fit=\"{fit}\"", size="xs", color="muted",
                        classes="font-mono")


def article() -> None:
    with ui.card(padding="none", classes="w-full max-w-2xl overflow-hidden"):
        ui.image("https://picsum.photos/seed/offsite/1200/500",
                 alt="The team on the terrace during the spring offsite",
                 ratio="wide")
        with ui.vstack(gap="xs", classes="p-5"):
            ui.text("Company news · 4 min read", size="sm", color="primary")
            ui.heading("What we learned at our spring offsite", level=3, size="xl")
            ui.text("Three days, twenty-two people and one decision: we are "
                    "shipping the mobile app in June.", color="muted")


def people() -> None:
    with ui.hstack(gap="lg", wrap=True, justify="center"):
        for name, role in (("Maya Chen", "Design"), ("Idris Okafor", "Engineering"),
                           ("Lena Novak", "Support")):
            with ui.vstack(gap="xs", align="center", classes="w-28"):
                ui.image(f"https://i.pravatar.cc/192?u={name}", alt=name,
                         ratio="square", classes="rounded-full")
                ui.text(name, size="sm", weight="medium")
                ui.text(role, size="xs", color="muted")


def page() -> None:
    page_header("image", "Image", SUMMARY)
    example("Four ratios", ratios, full=True,
            note="ratio= reserves the box before the file arrives, so nothing "
                 "below it moves when it loads.")
    example("Product cards", product_cards)
    example("Cover or contain", fits,
            note="cover fills the box and crops; contain shows the whole picture.")
    example("An article header", article,
            note="A wide banner on top of a card, edge to edge.")
    example("Team portraits", people)
