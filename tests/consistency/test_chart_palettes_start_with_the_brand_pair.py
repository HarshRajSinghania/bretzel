"""Gate — a chart's automatic series colours start with the brand pair.

Le défaut qu'elle ferme (2026-09-29)
--------------------------------------
Sans ``Series(color=…)``, un graphique prend ses couleurs dans le cycle
``THEME["palette"]``. Le cycle valait ``primary → success → warning →
info → error → muted`` : sous une identité verte (``Forest`` dans la
vitrine, ``primary`` == ``success`` au caractère près), les deux
premières séries sortaient du MÊME vert. Mesuré dans Chromium : une seule
couleur de remplissage pour deux séries.

``test_palette_distinctness`` ne pouvait rien y voir, et à raison : il
garantit que les couleurs du thème LIVRÉ diffèrent entre elles. Une app
redéfinit ``primary`` comme elle veut ; ce qui reste vrai sous n'importe
quelle identité, c'est que son auteur a choisi ``primary`` et
``secondary`` comme une PAIRE. Ce sont donc les deux seules couleurs que
le framework peut croire distinctes l'une de l'autre.

Les deux invariants
--------------------
1. **Le cycle ouvre sur la paire de marque**, et les couleurs de statut
   (``success``/``warning``/``error``) viennent après : elles portent un
   sens (« bon », « attention », « alarme ») qu'une série quelconque ne
   doit pas emprunter la première — ``error`` la dernière des trois,
   une série rouge se lisant comme une alerte.
2. **Les cycles sont identiques d'un graphique à l'autre.** Ils sont
   RECOPIÉS dans chaque thème (un thème reste self-contained) — une
   convention recopiée dérive, celle-ci est donc gatée.
"""

from __future__ import annotations

from tests.consistency._discovery import public_component_classes, ui_name_of

_BRAND = ("primary", "secondary")
_STATUS = ("success", "warning", "error")

#: Mesuré le 2026-09-29 : bar, line, scatter, pie.
_FLOOR = 4


def palettes() -> dict[str, tuple[str, ...]]:
    """``ui.<nom> → cycle`` pour chaque composant public qui en déclare un."""
    found: dict[str, tuple[str, ...]] = {}
    for cls in public_component_classes():
        theme = getattr(cls, "THEME", None)
        if isinstance(theme, dict) and "palette" in theme:
            found[ui_name_of(cls)] = tuple(theme["palette"])
    return found


def misordered(palette: tuple[str, ...]) -> list[str]:
    """Ce qui ne va pas dans UN cycle — vide quand il est juste.

    Le DÉTECTEUR, extrait pour être attaqué directement par la mutation.
    """
    faults: list[str] = []
    if palette[: len(_BRAND)] != _BRAND:
        faults.append(f"ouvre sur {palette[:len(_BRAND)]}, pas sur {_BRAND}")
    if "error" in palette and palette.index("error") < max(
        palette.index(c) for c in _STATUS if c in palette
    ):
        faults.append("`error` avant une autre couleur de statut")
    return faults


def test_the_sweep_is_not_vacuous() -> None:
    """① Le plancher, lu sur LA découverte de cette gate."""
    assert len(palettes()) >= _FLOOR, (
        f"seulement {len(palettes())} cycles trouvés ({_FLOOR} le "
        f"2026-09-29) : la découverte est cassée."
    )


def test_every_cycle_opens_on_the_brand_pair() -> None:
    """② L'interdiction."""
    bad = {name: f for name, p in palettes().items() if (f := misordered(p))}
    assert not bad, (
        f"des cycles de séries n'ouvrent pas sur la paire de marque : {bad}.\n"
        f"Sous une identité dont `primary` ressemble à une couleur de "
        f"statut (un vert, un rouge), deux séries sortiraient de la même "
        f"couleur."
    )


def test_the_cycles_agree() -> None:
    """② bis — recopiés d'un thème à l'autre, ils vont ensemble."""
    distinct = set(palettes().values())
    assert len(distinct) == 1, (
        f"les cycles de séries ont divergé : {palettes()}. Deux graphiques "
        f"côte à côte colorieraient différemment la même série."
    )


def test_the_detector_still_bites() -> None:
    """③ La mutation, dans les deux sens."""
    # L'ancien cycle, celui du défaut mesuré.
    assert misordered(("primary", "success", "warning", "info", "error"))
    # La paire inversée n'est plus « primary d'abord ».
    assert misordered(("secondary", "primary", "info"))
    # Le rouge avant les autres statuts.
    assert misordered(("primary", "secondary", "error", "success", "warning"))
    # Le versant LICITE : le cycle livré passe.
    assert not misordered(
        ("primary", "secondary", "info", "success", "warning", "error", "muted")
    )
