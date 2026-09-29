"""``/audio`` — the native audio player, controls on by default."""

from bretzel import ui
from examples.showcase.lib.example import example, page_header

SUMMARY = ("The browser's own audio player: visible controls by default, "
           "loop and muted when you need them.")

ROAR = "https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3"


def podcast() -> None:
    with ui.card(padding="md", classes="w-full max-w-lg"), ui.vstack(gap="md"):
        with ui.hstack(gap="md"):
            ui.image("https://picsum.photos/seed/podcast/160/160",
                     alt="Cover of The Back Office", ratio="square",
                     classes="w-16 shrink-0")
            with ui.vstack(gap="none"):
                ui.text("The Back Office · Episode 42", size="sm", color="muted")
                ui.text("Why your ops team still lives in spreadsheets",
                        weight="semibold")
        ui.audio(ROAR, classes="w-full")


def voice_note() -> None:
    with ui.vstack(gap="sm", classes="w-full max-w-md"):
        with ui.hstack(gap="sm", align="start"):
            ui.avatar(name="Idris Okafor", src="https://i.pravatar.cc/96?u=Idris",
                      size="sm")
            with ui.card(padding="sm"), ui.vstack(gap="xs"):
                ui.text("Idris Okafor · 09:41", size="xs", color="muted")
                ui.audio(ROAR)
        ui.text("Voice message · 0:02", size="xs", color="muted", align="right")


SOUNDS = [("Order received", "shopping-bag", "Plays when a new order arrives"),
          ("Build failed", "circle-x", "Plays when a deploy fails"),
          ("Timer finished", "timer", "Plays at the end of a focus block")]


def sound_settings() -> None:
    with ui.card(padding="md", classes="w-full max-w-2xl"), ui.vstack(gap="md"):
        ui.heading("Notification sounds", level=3, size="md")
        for label, icon, hint in SOUNDS:
            with ui.hstack(gap="md", justify="between", wrap=True):
                with ui.hstack(gap="sm"):
                    ui.icon(icon, color="primary")
                    with ui.vstack(gap="none"):
                        ui.text(label, weight="medium", size="sm")
                        ui.text(hint, size="xs", color="muted")
                ui.audio(ROAR, classes="w-72 shrink-0")


def ambience() -> None:
    with ui.vstack(gap="sm", align="center"):
        ui.text("Focus room — background loop", weight="medium")
        ui.audio(ROAR, loop=True, muted=True)
        ui.text("Starts muted; unmute from the player.", size="sm", color="muted")


def page() -> None:
    page_header("audio", "Audio", SUMMARY)
    example("A podcast episode", podcast,
            note="Controls are on by default: an audio element without them "
                 "is invisible.")
    example("A voice message", voice_note)
    example("Sound settings", sound_settings,
            note="One player per row, so each sound can be previewed in place.")
    example("A muted loop", ambience,
            note="loop=True replays forever; muted=True waits for the user to "
                 "turn the sound on.")
