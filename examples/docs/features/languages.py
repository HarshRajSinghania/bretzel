"""TOPIC — Speaking the visitor's language.

The split is clear-cut, and it is what must be understood before writing
a line:

- **the framework translates ITS sentences** — "Go to slide 3", "Maximum
  size 8 MB", the accessibility labels nobody writes by hand. It is
  ``bretzel.render.text``, and an app has nothing to do to benefit;
- **the app translates ITS OWN.** Bretzel does not know them and never
  will. It provides the seam: ``Language().code``.

⚠️ This is NOT an i18n library. No `.po` files, no plurals, no localised
dates beyond what the browser does. The roadmap announces it in 2.1 —
this chapter describes what EXISTS.
"""

from __future__ import annotations

from bretzel import page, ui
from examples.docs.features.shell import shell

PATH = "/languages"


@page(PATH, layout=shell, title="The languages · Bretzel docs",
      description="Internationalisation in Bretzel: the framework translates its own messages, and your app translates its own.")
def languages_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading("Speaking the visitor's language", level=1,
                       size="3xl")
            ui.text(
                'Two halves, and only one is yours: the framework '
                'translates its own sentences, your app translates its '
                'own.',
                color="muted", size="lg",
            )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('What the framework does on its own',
                               level=2)
                    ui.text(
                        "The sentences Bretzel produces — a carousel's "
                        "accessibility labels, a `file_upload`'s maximum-"
                        "size message, an empty table's text — go through "
                        "its own table. Declare the app's languages, and "
                        'they follow.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        'app = Bretzel(\n    secret_key="…",\n    lang="en",                  # the default language\n    languages=("en", "fr"),     # the ones we accept\n)\n',
                        lang="python",
                    )
                    ui.text(
                        'The language is resolved PER REQUEST: an explicit'
                        " choice wins over the browser's header, and a "
                        'language one has not declared falls back to the '
                        'default rather than rendering a raw key.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('What your app must do', level=2)
                    ui.text(
                        '`Language()` reads like its three ambient sisters'
                        ' — `Screen()`, `ColorScheme()`, '
                        '`LiveConnection()`: one object, one field. The '
                        'table is yours.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        'from bretzel import Language\n\nPHRASES = {\n    "en": {"save": "Save", "cancel": "Cancel"},\n    "fr": {"save": "Enregistrer",\n            "cancel": "Annuler"},\n}\n\ndef say(key: str) -> str:\n    """A function, not a component: this is TEXT, and\n    it must be able to go into a `placeholder=` as\n    much as into a `ui.text`."""\n    code = Language().code.split("-")[0]\n    return PHRASES.get(code, PHRASES["en"])[key]\n\nui.button(say("save"), color="primary")\n',
                        lang="python",
                    )
                    ui.text(
                        '`Language().code` can carry a region (`fr-CA`, '
                        '`en-GB`). Cutting at the hyphen is the simplest '
                        'form that works; keeping the region only makes '
                        'sense if the table really distinguishes it.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading("Letting the user choose", level=2)
                    ui.text(
                        '`Language.set` is a SERVER handler: it picks the '
                        'language and reloads the page in it. So one '
                        'passes it as a `partial`, not as a call — '
                        '`Language.set("fr")` would run at RENDER time, '
                        'not on the click.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        'from functools import partial\n\nui.button("English", on_click=partial(Language.set, "en"))\nui.button("Français", on_click=partial(Language.set, "fr"))\n',
                        lang="python",
                    )
                    ui.text(
                        'Why this exists when the language is already '
                        'automatic: `Accept-Language` describes the '
                        "operating system's configuration, not a reading "
                        'choice. With no way of saying otherwise, somebody'
                        ' whose machine is in English cannot read in '
                        'French.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('What it does not do', level=2)
                    ui.alert(
                        'This is not an i18n library. No `.po` files, no '
                        'plural rules, no string extraction, no date or '
                        'currency formatting beyond what the browser can '
                        "do. It is a SEAM: the request's language, and the"
                        " framework's table for its own words. The roadmap"
                        ' announces full i18n in 2.1.',
                        color="warning", title='A seam, not a library',
                    )
                    ui.text(
                        'That split is a choice, not a lack of time: an '
                        "app's sentences belong to it, and a framework "
                        'imposing its catalogue format would impose its '
                        'tooling too.',
                        color="muted", size="sm",
                    )
