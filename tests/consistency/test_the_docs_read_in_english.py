"""Gate : la documentation publique se lit en anglais, de bout en bout.

Décidé le 2026-09-26 : ``examples/docs`` est en anglais seul. Elle avait
été bilingue, et le mode français restait de toute façon un mélange — tout
ce qu'elle lit en direct dans le framework (capacités, arbre des paquets,
composants) n'existe qu'en anglais.

Ce que la gate garde, c'est ce que l'utilisateur a vu deux fois à
l'écran : des phrases françaises dans une page anglaise, par dizaines,
qu'aucune suite ne remarquait parce qu'aucune ne LISAIT le texte rendu.
Elle rend donc chaque route publique de la doc et lit ce qui s'affiche,
pas le source — une chaîne française peut arriver par une f-string, une
table, un libellé de colonne ou un helper de ``lib/``.

Le détecteur ne cherche que deux marques sûres du français : une lettre
accentuée propre au français, et une élision (``l'app``, ``qu'il``,
``d'une``). Un mot français sans l'une ni l'autre (« Forme », « Si »)
lui échappe ; c'est le prix d'un détecteur sans faux positif sur de
l'anglais. Les blocs de code sont exclus : le chapitre ``/languages``
montre légitimement une table ``"fr"``.
"""

from __future__ import annotations

import functools
import re
import warnings
from html.parser import HTMLParser
from typing import Final

from fastapi.testclient import TestClient

#: Lettres accentuées du français, absentes de l'anglais courant. Les
#: exceptions anglaises réelles sont dans :data:`_ENGLISH_LOANWORDS`.
_FRENCH: Final[re.Pattern[str]] = re.compile(
    r"[àâçéèêëîïôûùüœ]|\b(?:[ldnsjcm]|qu|jusqu|lorsqu|puisqu)['\u2019][a-zà-ÿ]",
    re.IGNORECASE,
)

#: Mots anglais qui portent un accent. Une entrée ici se justifie par un
#: vrai emploi anglais, pas par le confort de la gate.
_ENGLISH_LOANWORDS: Final[frozenset[str]] = frozenset({"bézier"})

#: Les routes publiques rendues. Mesuré à la création : 30.
_ROUTES_FLOOR: Final[int] = 25


class _VisibleText(HTMLParser):
    """Le texte qu'un lecteur voit, attributs lisibles compris, code exclu."""

    _HIDDEN = frozenset({"script", "style", "code", "pre", "template"})

    def __init__(self) -> None:
        super().__init__()
        self._hidden = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._HIDDEN:
            self._hidden += 1
        if not self._hidden:
            self.chunks += [v for k, v in attrs
                            if k in ("placeholder", "aria-label", "title", "alt") and v]

    def handle_endtag(self, tag: str) -> None:
        if tag in self._HIDDEN and self._hidden:
            self._hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self._hidden and data.strip():
            self.chunks.append(data.strip())


def french_in(text: str) -> bool:
    cleaned = text
    for word in _ENGLISH_LOANWORDS:
        cleaned = re.sub(word, "", cleaned, flags=re.IGNORECASE)
    return bool(_FRENCH.search(cleaned))


@functools.cache
def rendered_pages() -> dict[str, list[str]]:
    """Chaque route du sitemap, rendue, réduite à son texte visible."""
    from examples.docs.main import app

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with TestClient(app) as client:
            sitemap = client.get("/sitemap.xml").text
            routes = sorted(
                "/" + loc.split("/", 3)[3] if loc.count("/") > 2 else "/"
                for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap)
            )
            pages = {}
            for route in routes:
                response = client.get(route)
                assert response.status_code == 200, f"{route} → {response.status_code}"
                parser = _VisibleText()
                parser.feed(response.text)
                pages[route] = parser.chunks
    return pages


def test_every_public_route_is_read() -> None:
    pages = rendered_pages()
    assert len(pages) >= _ROUTES_FLOOR, f"seulement {len(pages)} routes rendues"
    empty = [route for route, chunks in pages.items() if len(chunks) < 10]
    assert not empty, f"des pages ne rendent presque aucun texte : {empty}"


def test_no_page_shows_french() -> None:
    found = [
        f"{route}  «{chunk[:100]}»"
        for route, chunks in rendered_pages().items()
        for chunk in chunks
        if french_in(chunk)
    ]
    assert not found, (
        f"{len(found)} fragment(s) français dans la documentation, qui est "
        "en anglais seul :\n  " + "\n  ".join(found)
    )


def test_the_detector_still_bites() -> None:
    for french in ("Ce qu'il faut savoir avant", "L'instance", "Structure d'app",
                   "Les 11 rôles de couleur", "déclaration refusée"):
        assert french_in(french), f"« {french} » n'est plus vu"
    for english in ("the curve goes Bézier instead of straight segments",
                    "it's the scope you need", "don't write this",
                    "The app's structure", "Cheat sheet"):
        assert not french_in(english), f"« {english} » est pris pour du français"
