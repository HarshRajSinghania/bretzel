"""Un passage de lint paie chaque coût UNE fois : le corpus, chaque arbre, le catalogue.

Ce que cette gate ferme
-----------------------

``bretzel.lint.run`` fait juger chaque module par dix-huit règles. Trois
coûts sont les mêmes pour tous les modules d'un passage, et rien
n'oblige une règle à s'en souvenir — une règle qui l'oublie ralentit le
passage sans qu'aucun test ne rougisse : le verdict est identique, seul
le temps change.

- **Le corpus.** `value-outside-the-table` doit savoir ce qu'un
  ``Theme(components=…)`` déclare *ailleurs*. Mesuré le 2026-08-27 : elle
  reparcourait les 322 fichiers d'``examples/`` pour chacun d'eux —
  56 s, quadratique. Tenu par ``corpus.derived``.
- **Chaque arbre.** Mesuré le 2026-09-27 : chaque règle reparcourait tout
  le fichier de son côté, ~25 parcours par module, 70 % d'un passage.
  Tenu par ``Module.nodes``, parcouru une fois et partagé.
- **Le catalogue des composants.** Même date : 110 000 cartes lues pour
  114 symboles, une par module ou par appel ``ui.*``. Tenu par
  ``corpus.catalogue()``, lu une fois par passage.

Ensemble : ``bretzel check examples`` passait de 15,8 s à 5,7 s, mêmes
constats à l'octet sur 1 522 fichiers.

Ce qu'on compte, et pourquoi pas le temps
-----------------------------------------

Un seuil en secondes ne veut rien dire ici — la machine dérive d'un
facteur 2 à 3 entre deux exécutions (memory
``inprocess_ab_or_no_measurement``). On compte, et on compte à un point
par où TOUT passe, pour ne pas surveiller une orthographe :

- les nœuds visités, par ``ast.iter_child_nodes`` : ``ast.walk`` l'appelle,
  une descente récursive écrite à la main aussi, et un ``from ast import
  walk`` ne l'évite pas ;
- les cartes construites, par ``ComponentInfo`` / ``HelperInfo`` : quel que
  soit le chemin d'import de ``describe_ui_symbol``, une carte en est une.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

import bretzel.lint
from bretzel.introspect import ComponentInfo, HelperInfo, ui_symbol_names
from bretzel.lint import corpus as lint_corpus
from bretzel.lint import run
from bretzel.lint.rules import kwargs, variant
from tests.consistency._discovery import EXAMPLES_FLOOR, REPO_ROOT

EXAMPLES = REPO_ROOT / "examples"

#: Le corpus des mutations — assez grand pour que quadratique se voie,
#: assez petit pour que le versant fautif reste payable.
#: ⚠️ **Troisième adresse en deux semaines** : ``examples/flat`` jusqu'à
#: l'élagage du 2026-09-07, puis ``mad`` jusqu'à celui du 2026-09-10.
#: Un corpus de mutation ancré sur une app de DÉMO est repris à chaque
#: fois qu'une démo tombe — et une démo est là pour pouvoir tomber.
#: `crm` est l'instrument d'usage réel, pas une démo : c'est la seule
#: adresse d'`examples/` qui ne relève pas de la règle d'élagage.
SMALL = REPO_ROOT / "examples" / "crm"

#: Nœuds visités par nœud du corpus. ``Module.nodes`` en visite chacun
#: une fois ; le reste, ce sont les sous-arbres qu'une règle relit à
#: dessein (le corps d'une fonction, les arguments d'un appel). Mesuré
#: 1,53 le 2026-09-27 : UNE règle qui reparcourt tout le fichier ajoute 1,
#: la borne ne laisse donc passer aucun reparcours complet.
VISITS_PER_NODE = 2

#: Les lectures du catalogue ENTIER qu'un passage a le droit de payer :
#: ``corpus.catalogue`` et les deux vocabulaires qu'en tire
#: l'introspection (``prop_vocabulary``, ``theme_vocabulary``), chacun
#: une fois par passage. Aucun ne dépend du nombre de fichiers.
CATALOGUE_READS_PER_PASS = 3
CARDS_BOUND = CATALOGUE_READS_PER_PASS * len(ui_symbol_names())


@dataclass
class Counts:
    scanned: int = 0
    nodes: int = 0
    visits: int = 0
    cards: int = 0
    declared_in: int = 0


def counted_pass(
    paths: tuple[Path, ...],
    *,
    monkeypatch: pytest.MonkeyPatch,
    rules: tuple[str, ...] | None = None,
) -> Counts:
    """Un passage, et ce qu'il a payé.

    Extrait pour être MUTABLE : les versants fautifs rejouent le même
    comptage avec une mémoire débranchée ou l'orthographe d'avant.
    """
    counts, seen = Counts(), []
    real_children = ast.iter_child_nodes
    real_modules = bretzel.lint.modules
    real_declared_in = variant._declared_in

    def counting_children(node):  # type: ignore[no-untyped-def]
        counts.visits += 1
        return real_children(node)

    def capturing_modules(paths):  # type: ignore[no-untyped-def]
        seen.extend(real_modules(paths))
        return seen

    def counting_declared_in(module):  # type: ignore[no-untyped-def]
        counts.declared_in += 1
        return real_declared_in(module)

    for card in (ComponentInfo, HelperInfo):
        real_init = card.__init__

        def counting_init(self, *args, _real=real_init, **kw):  # type: ignore[no-untyped-def]
            counts.cards += 1
            _real(self, *args, **kw)

        monkeypatch.setattr(card, "__init__", counting_init)
    monkeypatch.setattr(ast, "iter_child_nodes", counting_children)
    monkeypatch.setattr(bretzel.lint, "modules", capturing_modules)
    monkeypatch.setattr(variant, "_declared_in", counting_declared_in)
    report = run(list(paths), rules=rules)
    monkeypatch.undo()

    counts.scanned = report.files_scanned
    counts.nodes = sum(len(m.nodes) for m in seen)
    return counts


@pytest.fixture(scope="module")
def measured() -> Counts:
    """Un SEUL passage, toutes règles, sur ``examples/`` pour le plancher
    et les trois interdictions — aucune règle n'y échappe."""
    with pytest.MonkeyPatch.context() as patch:
        return counted_pass((EXAMPLES,), monkeypatch=patch)


def test_the_sweep_is_not_vacuous(measured: Counts) -> None:
    """Le plancher lit la découverte de CETTE gate, pas un ``rglob`` frais
    (memory ``gate_floors_must_read_the_gate_source``)."""
    assert measured.scanned >= EXAMPLES_FLOOR, (
        f"`examples/` n'a été balayé que sur {measured.scanned} fichiers — "
        "la gate ne mesure plus rien de significatif."
    )
    assert measured.visits and measured.cards and measured.declared_in, (
        f"un compteur ne voit plus rien passer : {measured}"
    )


def test_the_union_is_derived_once_not_once_per_module(measured: Counts) -> None:
    """La borne est ``scanned + 1`` : la dérivation parcourt les ``scanned``
    arbres du corpus, et le ``+ 1`` laisse la place à un module hors
    corpus (le repli documenté dans ``_declared_everywhere``)."""
    assert measured.declared_in <= measured.scanned + 1, (
        f"{measured.declared_in} lectures des thèmes pour {measured.scanned} "
        "fichiers — la règle re-dérive le corpus par module. Passer par "
        "`bretzel.lint.corpus.derived`."
    )


def test_each_tree_is_walked_once(measured: Counts) -> None:
    assert measured.visits <= VISITS_PER_NODE * measured.nodes, (
        f"{measured.visits} nœuds visités pour {measured.nodes} — une règle "
        "reparcourt tout l'arbre de son côté. Itérer `module.nodes`, pas "
        "`ast.walk(module.tree)`."
    )


def test_the_catalogue_is_read_once_per_pass(measured: Counts) -> None:
    assert measured.cards <= CARDS_BOUND, (
        f"{measured.cards} cartes construites (au plus {CARDS_BOUND}) — une "
        "règle relit le catalogue par fichier ou par appel. Passer par "
        "`bretzel.lint.corpus.catalogue()` ou `derived`."
    )


def test_the_detector_still_bites_without_the_memo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La mémoire du passage débranchée, la dérivation redevient quadratique."""
    monkeypatch.setattr(lint_corpus, "derived", lambda key, build: build())
    monkeypatch.setattr(variant, "derived", lambda key, build: build())
    counts = counted_pass((SMALL,), monkeypatch=monkeypatch, rules=(variant.RULE,))
    assert counts.scanned >= 10, f"corpus de mutation trop maigre : {counts}"
    assert counts.declared_in > counts.scanned + 1, (
        "la mémoire débranchée n'a PAS rendu le passage quadratique — "
        f"{counts}. `derived` n'est plus le point de passage."
    )


def test_the_detector_sees_a_rule_that_walks_the_tree_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'orthographe d'avant : chaque accès à ``nodes`` reparcourt l'arbre."""
    monkeypatch.setattr(
        lint_corpus.Module, "nodes", property(lambda m: tuple(ast.walk(m.tree)))
    )
    counts = counted_pass((SMALL,), monkeypatch=monkeypatch)
    assert counts.visits > VISITS_PER_NODE * counts.nodes, (
        f"des parcours répétés passent sous la borne : {counts}"
    )


def test_the_detector_sees_a_card_read_per_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'orthographe d'avant, par le chemin qui échappait au premier
    compteur : une carte lue à chaque appel ``ui.*``, via le ré-export
    ``bretzel.introspect.describe_ui_symbol``."""
    from bretzel.introspect import RESERVED_KWARGS, describe_ui_symbol

    def accepted_per_call(ui_name: str):  # type: ignore[no-untyped-def]
        if ui_name not in ui_symbol_names():
            return None
        info = describe_ui_symbol(ui_name)
        if not isinstance(info, ComponentInfo):
            return kwargs._NOT_JUDGED
        return frozenset({p.name for p in info.params} | set(RESERVED_KWARGS))

    monkeypatch.setattr(kwargs, "_accepted", accepted_per_call)
    counts = counted_pass((SMALL,), monkeypatch=monkeypatch, rules=(kwargs.RULE,))
    assert counts.cards > CARDS_BOUND, (
        f"une carte lue par appel passe sous la borne : {counts}"
    )


def test_a_rule_called_outside_run_still_sees_its_own_module() -> None:
    """Le versant LICITE : hors passage, rien n'est mémorisé et rien ne
    manque. Un cache global rendrait la dérivation d'un AUTRE corpus, un
    ``ContextVar`` mal réinitialisé la rendrait vide ; ``nodes`` et le
    catalogue doivent se calculer sur un ``Module`` fabriqué."""
    source = (
        "from bretzel import ui, Theme\n"
        'THEME = Theme(components={"button": {"variants": {"maison": "bg-x"}}})\n'
        'ui.button("ok", variant="maison", nope=1)\n'
    )
    module = lint_corpus.Module(
        path=Path("fictif.py"), tree=ast.parse(source), source=source
    )
    assert lint_corpus.current() == (), "ce test doit tourner hors `run`"
    declared = variant._declared_everywhere(module)
    assert "maison" in declared.get("button", {}).get("variants", set()), (
        "hors `run`, la règle ne voit plus la variante déclarée par son "
        "propre module — elle condamnerait la forme recommandée."
    )
    assert [f.line for f in kwargs.check(module)] == [3], (
        "hors `run`, `unknown-kwarg` ne voit plus `nope=`."
    )
