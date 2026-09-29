"""Une expression cliente arrive ENTIÈRE dans l'attribut qui la porte.

Un binding atterrit dans un attribut ``bz-*`` sous la forme d'une
expression JS. Celle d'un champ nu ne contient que des identifiants, mais
celle d'une :class:`ClientExpression` porte des littéraux —
``busy.then_else("moon", "circle-check")`` produit
``($bz.state.P.default.busy ? "moon" : "circle-check")``, avec des
guillemets DOUBLES, ceux qui délimitent la valeur d'un attribut HTML.

``serialize_attrs`` les échappe en ``&quot;``, que le parseur rend au
runtime tels quels. Mais une sous-classe de ``str``, ``RawAttrValue``,
contournait cet échappement, et deux composants l'employaient pour leurs
expressions : ``ui.icon`` (``bz-attr:icon``) et ``ui.color_picker`` (dont
les nuanciers interpolent des valeurs de l'appelant). Elle est supprimée. Le
premier ``"`` refermait l'attribut, le reste devenait des attributs
parasites, et le runtime compilait ``$bz._resolveIcon(($bz.state… ? `` —
« Unexpected token ')' ». Mesuré le 2026-09-29 : l'exception tue le scan
de TOUTE la page, qui ne passe jamais ``bz-ready``.

La gate lie chaque prop bindable de chaque composant public à une
expression qui contient les quatre caractères qu'un attribut doit
échapper (``" ' & <``), rend le composant, relit le HTML avec le parseur
de la bibliothèque standard, et exige que tout attribut qui COMMENCE
l'expression la contienne en entier. Un attribut tronqué, c'est une
valeur refermée en route.
"""

from __future__ import annotations

from html.parser import HTMLParser

import pytest

from bretzel.components.base.testing import render_isolated
from bretzel.core.serialize import serialize
from bretzel.state.scopes.client import ClientExpression
from tests.audit.test_binding_completeness import CONSTRUCT, _Skip
from tests.consistency._discovery import (
    assert_sweep_is_not_vacuous,
    public_component_classes,
)
from tests.consistency.test_binding_path_is_re_evaluated import _bindable_kwargs

#: La tête reconnaissable de l'expression, puis l'expression entière. Les
#: quatre caractères hostiles sont dans les deux branches du ternaire.
_HEAD = "($bz.state.probe.default.flag ?"
_EXPR = f"""{_HEAD} "a&b" : '<c>')"""


def _expression() -> ClientExpression:
    return ClientExpression(_EXPR, ssr_value="a&b")


class _Attributes(HTMLParser):
    """Toutes les valeurs d'attributs, décodées comme le navigateur."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.values.extend((name, value or "") for name, value in attrs)


def truncated_attributes(html: str) -> list[str]:
    """Les attributs où l'expression commence sans finir.

    Extrait pour être muté (``test_the_detector_still_bites``).
    """
    parser = _Attributes()
    parser.feed(html)
    return [
        f"{name}={value!r}"
        for name, value in parser.values
        if _HEAD in value and _EXPR not in value
    ]


def _render_bound(cls: type, prop: str) -> str:
    builder = CONSTRUCT.get(cls.__name__)
    with render_isolated():
        comp = (builder(cls, prop, _expression()) if builder is not None
                else cls(**{prop: _expression()}))
        return serialize(comp.render())


_CASES = [
    (cls, prop)
    for cls in public_component_classes()
    for prop in _bindable_kwargs(cls)
]


@pytest.mark.parametrize(
    "cls,prop", _CASES, ids=lambda v: v if isinstance(v, str) else v.__name__
)
def test_a_bound_expression_is_not_cut_by_its_quotes(cls: type, prop: str) -> None:
    try:
        html = _render_bound(cls, prop)
    except _Skip as exc:
        pytest.skip(str(exc))
    except Exception as exc:
        # Une prop qui refuse une EXPRESSION (two-way : il faut un champ
        # à écrire) sort ici — c'est un refus définitionnel, et le
        # plancher ci-dessous vérifie qu'il en reste assez pour mordre.
        pytest.skip(f"{cls.__name__}.{prop} refuse une expression : "
                    f"{type(exc).__name__}")

    cut = truncated_attributes(html)
    assert not cut, (
        f"{cls.__name__}.{prop}= : l'expression liée sort TRONQUÉE de son "
        f"attribut —\n  {cut[0]}\n\n"
        f"Un `\"` de l'expression a refermé la valeur : elle a été émise sans "
        f"passer par `escape_attr`. Émets une `str` ordinaire et laisse "
        f"`serialize_attrs` l'échapper — le navigateur rend `&quot;` au "
        f"runtime tel quel."
    )


def test_the_sweep_reaches_the_expressions() -> None:
    """Plancher : le balayage voit l'expression ressortir, et là où elle a
    cassé. Sans lui, un rendu qui n'émettrait plus l'expression (ou une
    tête renommée) passerait pour « aucune troncature »."""
    assert_sweep_is_not_vacuous()
    assert len(_CASES) >= _CASE_FLOOR, len(_CASES)
    reached: set[str] = set()
    for cls, prop in _CASES:
        try:
            html = _render_bound(cls, prop)
        except Exception:
            continue
        parser = _Attributes()
        parser.feed(html)
        if any(_EXPR in value for _, value in parser.values):
            reached.add(cls.__name__)
    assert len(reached) >= _REACHED_FLOOR, sorted(reached)
    # Celui qui passait par le contournement, et un composant qui le
    # construit pour ses icônes.
    assert {"Icon", "Badge"} <= reached, sorted(reached)


# Mesuré le 2026-09-29 : 102 couples, 41 composants où l'expression ressort.
_CASE_FLOOR = 40
_REACHED_FLOOR = 30


def test_the_detector_still_bites() -> None:
    """Les deux versants : une valeur refermée par son `"` est vue ; la
    même, échappée, ne l'est pas."""
    raw = f'<i bz-attr:icon="$bz._resolveIcon({_EXPR}, \'lucide\')"></i>'
    assert truncated_attributes(raw), "une valeur refermée doit mordre"

    escaped = _EXPR.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    licit = f'<i bz-attr:icon="$bz._resolveIcon({escaped}, \'lucide\')"></i>'
    assert not truncated_attributes(licit), "échappée, elle est entière"
