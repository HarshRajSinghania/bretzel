"""``ui.file_upload(paste=True)`` — a Ctrl+V in the form joins the file.

The gap it closes
-----------------
A screenshot is on the clipboard (Win+Shift+S, Cmd+Ctrl+Shift+4) and
the person is writing in the form's field: the only ways to attach it
were to save it to disk, then pick or drop it. Asked on 2026-09-27 for
the atelier of ``bretzel-product``, whose question field sits above a
``list="chips"`` picker.

Why in the BROWSER
------------------
Everything that matters happens there: the paste fires on the focused
field, not on the picker; the file must reach the hidden
``<input type=file>`` (what the form submits); and a paste that carries
text must still write its text. A render test would see one attribute.

Heavy (uvicorn + Chromium) — run explicitly ::

    py -m pytest tests/runtime_js/test_a_pasted_file_joins_the_picker.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from tests.audit.harness import audit_server, browser_page

app = Bretzel(secret_key="p" * 32, title="Bretzel · coller un fichier", mode="dev")


def sent() -> None:  # pragma: no cover — wired, never submitted here
    pass


@page("/")
def home() -> None:
    with ui.vstack(gap="lg", classes="p-8"):
        with ui.form(on_submit=sent, id="avec"):
            ui.textarea(id="champ")
            ui.file_upload(variant="button", list="chips", multiple=True,
                           name="pieces", paste=True, id="colle")
        with ui.form(on_submit=sent, id="sans"):
            ui.textarea(id="champ-sans")
            ui.file_upload(variant="button", list="chips", multiple=True,
                           name="autres", id="ignore")


app.include(__name__)

#: Paste into ``field``: a clipboard of ``files`` (name, type), plus
#: ``text`` when given — what the OS puts there, built by hand.
_PASTE = """([field, files, text]) => {
  const dt = new DataTransfer();
  for (const [name, type] of files) {
    dt.items.add(new File(['x'], name, {type}));
  }
  if (text) dt.setData('text/plain', text);
  const target = document.getElementById(field);
  target.focus();
  const evt = new ClipboardEvent('paste', {
    clipboardData: dt, bubbles: true, cancelable: true,
  });
  target.dispatchEvent(evt);
  return evt.defaultPrevented;
}"""

_FILES = """(name) => Array.from(
  document.querySelector(`input[type=file][name=${name}]`).files
).map((f) => f.name)"""


@pytest.fixture(scope="module")
def live():
    with audit_server(app) as url:
        with browser_page(url, "/") as pg:
            pg.wait_for_selector("html.bz-ready")
            pg.wait_for_timeout(400)
            yield pg


def files(pg, name: str) -> list[str]:
    return pg.evaluate(_FILES, name)


def test_a_screenshot_pasted_in_the_field_joins_the_picker(live) -> None:
    prevented = live.evaluate(_PASTE, ["champ", [["image.png", "image/png"]], ""])
    names = files(live, "pieces")
    assert len(names) == 1, (
        f"a screenshot pasted in the form's field did not reach the "
        f"picker's <input type=file>: {names}. The form would submit "
        f"nothing."
    )
    assert names[0].startswith("pasted-") and names[0].endswith(".png"), (
        f"the pasted screenshot kept the browser's name {names[0]!r}: "
        f"three captures would be three « image.png »."
    )
    assert prevented, "the paste was not consumed: the field would get it too"
    live.wait_for_selector("#colle >> text=/pasted-/", timeout=3_000)


def test_a_second_paste_adds_rather_than_replaces(live) -> None:
    live.evaluate(_PASTE, ["champ", [["image.png", "image/png"],
                                     ["devis.pdf", "application/pdf"]], ""])
    names = files(live, "pieces")
    assert len(names) == 3 and "devis.pdf" in names, (
        f"a copied file keeps its name, and a second paste adds: {names}"
    )


def test_a_paste_that_carries_text_is_left_to_the_field(live) -> None:
    """Excel cells come with a picture of themselves: they are TEXT."""
    before = files(live, "pieces")
    prevented = live.evaluate(
        _PASTE, ["champ", [["image.png", "image/png"]], "Dupont\t12"])
    assert files(live, "pieces") == before, (
        "a paste of text with a picture beside it joined the picture — "
        "pasting three Excel cells would attach an image of them."
    )
    assert not prevented, "the text of the paste would not reach the field"


def test_a_picker_without_paste_ignores_it(live) -> None:
    """Contrôle POSITIF of the opt-in: without it, nothing changes."""
    live.evaluate(_PASTE, ["champ-sans", [["image.png", "image/png"]], ""])
    assert files(live, "autres") == [], (
        "a picker WITHOUT paste=True took a paste: the prop would be "
        "decorative, and every form with a picker would swallow images."
    )
