"""Gate : la largeur d'un CADRE ne s'écrit pas en crans de densité.

Un cran d'espacement (``w-64``, ``h-72``) vaut ``calc(var(--spacing) * n)``,
et ``--spacing`` est la base de la DENSITÉ : 3 px par défaut depuis le
2026-09-13, et réglable par l'app. C'est voulu pour un contrôle — un champ
dense est un champ plus petit. C'est faux pour un cadre : une sidebar, un
tiroir, un dialogue ne rétrécissent pas parce que les boutons se serrent.

Mesuré le 2026-09-29 : la sidebar ``md`` (``w-64``) rendait 192 px au lieu
des 256 que son nom promet, le tiroir ``sm``/``md`` 25 % de moins que
``lg``/``xl``, écrits eux en ``rem`` — une échelle cassée en son milieu,
et un chrome qui « fait serré » sans qu'aucune classe ait l'air fausse.

La population : le groupe ``widths`` de chaque thème de composant — c'est
le vocabulaire où un thème nomme la LARGEUR de son cadre (container,
dialog, drawer, sidebar). Ce que la gate ne voit pas : une largeur de
cadre écrite hors d'un groupe ``widths`` (la pile des notifications, en
``rem`` depuis la même date, a été corrigée à la main).
"""

from __future__ import annotations

import re

from tests.consistency._discovery import public_component_classes, ui_name_of

#: Un utilitaire de dimension exprimé en crans : ``w-64``, ``max-h-96``,
#: ``md:w-80``, ``size-72``. ``w-[16rem]``, ``max-w-5xl``, ``w-full`` et
#: ``w-screen`` ne sont pas des crans.
_STEP_SIZE = re.compile(r"^(?:[\w-]+:)*(?:min-|max-)?(?:w|h|size)-\d+(?:\.\d+)?!?$")

#: Mesuré à la création : 4 thèmes portent un groupe ``widths``.
_THEMES_FLOOR = 4


def width_groups() -> dict[str, object]:
    """``ui.<nom>`` → le groupe ``widths`` de son thème, pour ceux qui en ont un."""
    return {
        ui_name_of(cls): cls.THEME["widths"]
        for cls in public_component_classes()
        if isinstance(getattr(cls, "THEME", None), dict) and "widths" in cls.THEME
    }


def strings_in(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in strings_in(v)]
    return []


def step_sizes(classes: str) -> list[str]:
    """Le détecteur : les utilitaires de dimension écrits en crans."""
    return [token for token in classes.split() if _STEP_SIZE.match(token)]


def test_the_sweep_is_not_vacuous() -> None:
    groups = width_groups()
    assert len(groups) >= _THEMES_FLOOR, (
        f"seulement {len(groups)} thème(s) avec un groupe `widths` "
        f"({sorted(groups)}) — la découverte ne lit plus les thèmes."
    )
    assert sum(len(strings_in(g)) for g in groups.values()) >= 15


def test_no_frame_width_is_a_density_step() -> None:
    offenders = [
        f"ui.{name}: {token}"
        for name, group in sorted(width_groups().items())
        for classes in strings_in(group)
        for token in step_sizes(classes)
    ]
    assert not offenders, (
        "largeur(s) de cadre écrite(s) en crans de densité :\n  "
        + "\n  ".join(offenders)
        + "\n\nUn cran suit `--spacing` (3 px par défaut) : écris la "
        "largeur en `rem` (`w-[16rem]`) ou en conteneur (`max-w-3xl`)."
    )


def test_the_detector_still_bites() -> None:
    assert step_sizes("w-64 md:max-h-96 size-72 min-w-48!") == [
        "w-64", "md:max-h-96", "size-72", "min-w-48!",
    ]
    # Le versant qui épargne : ce qui n'est pas un cran.
    assert not step_sizes("w-[16rem] max-w-5xl w-full w-screen h-screen "
                          "max-w-[calc(100vw-2rem)] w-fit")
