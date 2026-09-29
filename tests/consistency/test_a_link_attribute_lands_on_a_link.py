"""Gate : un attribut de lien ne se pose que sur un lien.

``href`` / ``target`` / ``rel`` / ``download`` ne veulent rien dire hors
d'un ``<a>`` (ou d'un ``<area>``). Jusqu'au 2026-09-29, un composant qui
ne lisait pas ``href`` le laissait passer en attribut brut sur son
élément : ``ui.icon_button(href=…)`` rendait un ``<button href>`` mort,
et l'icône GitHub de la vitrine publique ne menait nulle part — sans
erreur, sans avertissement, sans qu'aucun contrôle ne le voie (le lint
l'admettait comme attribut brut déclaré).

Deux issues sont licites pour chaque composant public construit avec
``href="…"`` : il en fait un LIEN (l'attribut atterrit sur un ``<a>``),
ou il REFUSE (``ComponentUsageError`` / ``TypeError``). La troisième —
l'attribut posé sur autre chose qu'un lien — est ce que la gate interdit.
"""

from __future__ import annotations

from html.parser import HTMLParser

import pytest

from bretzel.components.base.attrs import ANCHOR_TAGS, ComponentUsageError
from tests.consistency._discovery import (
    public_component_classes,
    rendered_html_of,
    ui_name_of,
)

PROBE = "/bz-link-probe"

#: Mesuré à la création : 102 composants publics.
_FLOOR = 90


class _HrefCarriers(HTMLParser):
    """Les balises qui portent la sonde ``href``."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if ("href", PROBE) in attrs:
            self.tags.append(tag)


def stray_carriers(html: str) -> list[str]:
    """Le détecteur : les éléments NON-lien qui portent la sonde."""
    parser = _HrefCarriers()
    parser.feed(html)
    return [tag for tag in parser.tags if tag not in ANCHOR_TAGS]


def outcome(cls: type) -> str:
    """``link`` / ``refused`` / ``context`` / ``absent``, ou ``stray:<tags>``."""
    try:
        html = rendered_html_of(cls, prop="href", value=PROBE)
    except (ComponentUsageError, TypeError):
        return "refused"
    if html is None:
        return "context"
    stray = stray_carriers(html)
    if stray:
        return "stray:" + ",".join(stray)
    return "link" if PROBE in html else "absent"


_OUTCOMES = {ui_name_of(cls): outcome(cls) for cls in public_component_classes()}


def test_the_sweep_is_not_vacuous() -> None:
    assert len(_OUTCOMES) >= _FLOOR
    # Les deux issues licites existent, sinon la gate ne voit plus rien.
    assert "link" in _OUTCOMES.values()
    assert "refused" in _OUTCOMES.values()


@pytest.mark.parametrize("name", sorted(_OUTCOMES))
def test_a_link_attribute_lands_on_a_link(name: str) -> None:
    assert not _OUTCOMES[name].startswith("stray:"), (
        f"ui.{name}(href=…) pose l'attribut sur <{_OUTCOMES[name][6:]}>, où il "
        f"ne fait rien. Le composant doit en faire un lien, ou le refuser."
    )


def test_the_detector_still_bites() -> None:
    assert stray_carriers(f'<button href="{PROBE}">x</button>') == ["button"]
    assert stray_carriers(f'<div><span href="{PROBE}"></span></div>') == ["span"]
    # Le versant qui épargne : un vrai lien, ou un href qui n'est pas la sonde.
    assert not stray_carriers(f'<a href="{PROBE}">x</a>')
    assert not stray_carriers('<button href="/elsewhere">x</button>')
