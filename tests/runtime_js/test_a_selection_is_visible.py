"""Ce qui est sélectionné se VOIT — ``ui.toggle_group`` et ``ui.tree``, dans les deux thèmes.

Les deux composants marquaient leur sélection d'une teinte à 10 %
(``bg-(--bz-bg)``), mélangée vers la couleur de SURFACE. Posée sur ce qui
les entoure, elle disparaît :

- ``toggle_group`` — sur son rail ``bg-interface`` : 1,05:1 en clair,
  1,10:1 en sombre (mesuré le 2026-10-01). Le seul signal restant était
  la couleur du texte, qui ne dit rien quand le bouton porte un avatar :
  c'est le filtre d'assignation du kanban qui l'a montré. Réparé par un
  souligné, l'idiome des onglets.
- ``tree`` — sur la page ou dans une carte : la même teinte, plus un
  texte coloré et en gras, sans aucune marque qui tienne 3:1.

Ce que la gate exige n'est pas une classe mais une propriété : WCAG
1.4.11 demande 3:1 à l'indicateur d'état d'un contrôle contre ce qui
l'entoure. Sont candidats le fond de l'élément, ses bordures et son
pseudo-élément ``::before`` ; « ce qui l'entoure » est le premier ancêtre
au fond opaque — le rail du groupe, la carte, ou la page.

Les deux bras
-------------
L'élément sélectionné porte un indicateur à 3:1 au moins ; un élément
NON sélectionné n'en porte aucun. Sans le second, peindre la marque sur
tous les éléments ferait passer la gate et ne distinguerait plus rien.

Lourd (uvicorn + Chromium) — à lancer explicitement ::

    py -m pytest tests/runtime_js/test_a_selection_is_visible.py -q -m browser
"""

from __future__ import annotations

import pytest

from bretzel import Bretzel, page, ui
from tests.audit.harness import audit_server, browser_page

#: WCAG 1.4.11 — contraste d'un composant d'interface ou d'un état.
CONTRASTE_MINIMAL = 3.0

#: Chaque banc : (identifiant, sélecteur de ses éléments).
BANCS: tuple[tuple[str, str], ...] = (
    ("groupe-page", "button"),
    ("arbre-page", "[data-selected]"),
    ("groupe-carte", "button"),
    ("arbre-carte", "[data-selected]"),
)

app = Bretzel(secret_key="f" * 32, title="Bretzel · sélection", mode="dev")


def groupe(ident: str) -> None:
    ui.toggle_group(value="b", id=ident,
                    options=[("a", "Alpha"), ("b", "Beta"), ("c", "Gamma")])


def arbre(ident: str) -> None:
    with ui.tree(value="b", id=ident):
        ui.tree_node(value="a", label="Alpha")
        ui.tree_node(value="b", label="Beta")
        ui.tree_node(value="c", label="Gamma")


@page("/")
def home() -> None:
    # Deux voisinages : la page, et une carte — la teinte se mélange vers
    # la SURFACE, donc c'est sur la page qu'elle aurait le plus de chances
    # de se voir, et dans une carte qu'elle en a le moins.
    with ui.vstack(gap="lg", classes="p-4 w-[20rem]"):
        groupe("groupe-page")
        arbre("arbre-page")
        with ui.card(padding="md"), ui.vstack(gap="lg"):
            groupe("groupe-carte")
            arbre("arbre-carte")


app.include(__name__)


@pytest.fixture(scope="module")
def base_url():
    with audit_server(app) as url:
        yield url


#: Chaque couleur passe par un canevas : Chromium rend un ``color-mix``
#: calculé en ``color(srgb …)``, qu'aucune expression régulière sur
#: ``rgb()`` ne lirait. Le canevas, lui, rend toujours des octets.
MESURE = """([ident, selecteur]) => {
  const ctx = document.createElement('canvas')
    .getContext('2d', {willReadFrequently: true});
  const octets = (css) => {
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = '#000'; ctx.fillStyle = css; ctx.fillRect(0, 0, 1, 1);
    return [...ctx.getImageData(0, 0, 1, 1).data];
  };
  const lum = ([r, g, b]) => {
    const c = [r, g, b].map(v => v / 255).map(
      v => v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const contraste = (a, b) => {
    const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
    return (x + 0.05) / (y + 0.05);
  };
  const opaque = (css) => octets(css)[3] === 255;
  const entourage = (el) => {
    for (let n = el.parentElement; n; n = n.parentElement) {
      const fond = getComputedStyle(n).backgroundColor;
      if (opaque(fond)) return octets(fond);
    }
    return octets(getComputedStyle(document.body).backgroundColor);
  };
  const racine = document.getElementById(ident);
  return [...racine.querySelectorAll(selecteur)].map(el => {
    const s = getComputedStyle(el), avant = getComputedStyle(el, '::before');
    const autour = entourage(el);
    const candidats = [];
    if (opaque(s.backgroundColor)) candidats.push(s.backgroundColor);
    for (const cote of ['Top', 'Right', 'Bottom', 'Left'])
      if (parseFloat(s['border' + cote + 'Width']) >= 1
          && opaque(s['border' + cote + 'Color']))
        candidats.push(s['border' + cote + 'Color']);
    if (avant.content !== 'none' && avant.display !== 'none'
        && parseFloat(avant.width) >= 1 && opaque(avant.backgroundColor))
      candidats.push(avant.backgroundColor);
    return {
      texte: el.textContent.trim().slice(0, 12),
      choisi: el.getAttribute('data-selected') === 'true',
      meilleur: Math.max(1, ...candidats.map(c => contraste(octets(c), autour))),
    };
  });
}"""


def mesurer(pg, schema: str) -> dict[str, list[dict]]:
    pg.emulate_media(color_scheme=schema)
    pg.reload()
    pg.wait_for_selector("html.bz-ready")
    return {ident: pg.evaluate(MESURE, [ident, selecteur])
            for ident, selecteur in BANCS}


@pytest.mark.browser
@pytest.mark.parametrize("schema", ["light", "dark"])
def test_every_bench_has_one_selected_item(base_url: str, schema: str) -> None:
    """Plancher : chaque banc rend trois éléments, dont UN sélectionné.
    Sans lui, un rendu sans sélection — ou un sélecteur qui ne trouve plus
    rien — rendrait les deux bras d'à côté muets."""
    with browser_page(base_url, "/") as pg:
        bancs = mesurer(pg, schema)
    for ident, elements in bancs.items():
        assert len(elements) == 3, (ident, elements)
        assert [e["texte"] for e in elements if e["choisi"]] == ["Beta"], (
            ident, elements)


@pytest.mark.browser
@pytest.mark.parametrize("schema", ["light", "dark"])
def test_the_selected_item_carries_a_visible_mark(base_url: str,
                                                  schema: str) -> None:
    with browser_page(base_url, "/") as pg:
        bancs = mesurer(pg, schema)
    pales = [f"{ident} : {e['meilleur']:.2f}:1"
             for ident, elements in bancs.items()
             for e in elements if e["choisi"]
             and e["meilleur"] < CONTRASTE_MINIMAL]
    assert not pales, (
        f"[{schema}] la sélection ne se distingue pas de ce qui l'entoure — "
        f"il faut {CONTRASTE_MINIMAL}:1 (WCAG 1.4.11) :\n  "
        + "\n  ".join(pales)
        + "\nUne teinte mélangée vers la surface n'y arrive pas ; un trait "
          "dans le palier de texte accentué, si.")


@pytest.mark.browser
@pytest.mark.parametrize("schema", ["light", "dark"])
def test_an_unselected_item_carries_none(base_url: str, schema: str) -> None:
    with browser_page(base_url, "/") as pg:
        bancs = mesurer(pg, schema)
    marques = [f"{ident} : « {e['texte']} » à {e['meilleur']:.2f}:1"
               for ident, elements in bancs.items()
               for e in elements if not e["choisi"]
               and e["meilleur"] >= CONTRASTE_MINIMAL]
    assert not marques, (
        f"[{schema}] des éléments NON sélectionnés portent la marque — "
        f"elle ne distingue plus la sélection :\n  " + "\n  ".join(marques))
