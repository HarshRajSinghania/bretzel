"""Gate — aucun composant ne bâtit son ``bz-data`` à la main.

C'était la **dette n°1 du socle** : un composant à état client écrivait
son scope en concaténant une chaîne ``"{…$bz.<fabrique>.scope," + … +
"}"``, avec la même bascule « champ local → cellule du magasin » plus
``server_sync_marker``. Personne n'avait extrait le bloc, donc chaque
composant neuf en recopiait un : 5 en juillet, 15 en septembre.

Elle est payée d'un bloc depuis le 2026-09-26 : les quinze passent par
:func:`bretzel.components.base._wiring.scope_literal`. Les recopies ne
divergeaient pas que par la forme — la branche « lié » de ``ui.select``
et ``ui.combobox`` ne re-semait pas ses options, ce que
``tests/runtime_js/test_a_bound_list_follows_its_refreshed_options.py``
a mesuré dans un navigateur. C'est le coût d'une règle recopiée quinze
fois : chaque copie finit par en oublier un morceau.

**Pourquoi une détection par la FORME.** La liste de dette a menti trois
fois en un mois, toujours vers le bas, parce qu'on la comptait par NOM de
helper (``_build_bz_data``, ``_scope_literal``…) et que trois composants
assemblaient le littéral en ligne, sans helper nommé. Ce qui identifie un
scope bâti à la main, c'est la marque ``{...$bz.`` dans une source
Python. Renommer un helper ne la fait pas disparaître.

**Ce qui reste permis** : un littéral d'étalement PUR
(``"{...$bz.x.scope}"``) — il n'ajoute rien, donc rien à recopier.
"""

from __future__ import annotations

import functools
import re
from pathlib import Path

from tests.consistency._discovery import (
    assert_sweep_is_not_vacuous,
    component_sources,
)

_ROOT = Path(__file__).resolve().parents[2]

#: La marque d'un scope assemblé à la main : l'étalement de la fabrique
#: partagée dans un littéral d'objet JS. Indépendante du nom du helper.
_MARK = "{...$bz."

#: Ce qui n'est PAS fautif : un scope qui ÉTALE la fabrique partagée et
#: n'y ajoute rien. La forme fautive est un littéral qu'on COMPLÈTE.
_PURE_SPREAD = re.compile(r"^\{\.\.\.\$bz\.[A-Za-z0-9_.]+\}$")

#: Les littéraux de chaîne d'une source Python qui contiennent la marque.
_LITERAL = re.compile(r'"([^"\n]*\{\.\.\.\$bz\.[^"\n]*)"')

#: 256 modules de composant le 2026-09-26 — le plancher de CE balayage.
_SWEEP_FLOOR = 200


def hand_builds_a_scope(source: str) -> bool:
    """Cette source assemble-t-elle un ``bz-data`` à la main ?

    Oui dès qu'un littéral portant la marque n'est pas un étalement pur.
    Une source dont TOUS les littéraux marqués sont purs est propre.
    """
    if _MARK not in source:
        return False
    literals = _LITERAL.findall(source)
    if not literals:
        # La marque est là mais hors d'un littéral d'une seule ligne :
        # concaténation multi-lignes, f-string découpée… — donc bâti à
        # la main, et c'est le cas le plus fautif.
        return True
    return any(not _PURE_SPREAD.match(lit) for lit in literals)


@functools.lru_cache(maxsize=1)
def _sweep() -> tuple[int, frozenset[str]]:
    """``(modules lus, modules fautifs)``. Caché : deux tests le lisent,
    et le plancher doit compter CE balayage, pas en refaire un."""
    visited = 0
    found: set[str] = set()
    for path in component_sources():
        visited += 1
        if hand_builds_a_scope(path.read_text(encoding="utf-8-sig")):
            found.add(path.relative_to(_ROOT / "bretzel").as_posix())
    return visited, frozenset(found)


def test_the_sweep_reads_the_components() -> None:
    assert_sweep_is_not_vacuous()
    visited, _ = _sweep()
    assert visited >= _SWEEP_FLOOR, (
        f"le balayage n'a lu que {visited} modules de composant "
        f"(>= {_SWEEP_FLOOR} attendus) — une interdiction qui ne lit rien "
        f"passe aussi bien qu'une interdiction tenue."
    )


def test_no_component_hand_builds_its_scope() -> None:
    _, found = _sweep()
    assert not found, (
        f"{sorted(found)} assemblent leur `bz-data` à la main.\n"
        f"  Passe par `scope_literal` (`components/base/_wiring.py`) : "
        f"`slabs` pour l'étalement, `cell=` + `binding_path=` pour la "
        f"valeur, `config=` pour ce que le serveur re-sème, `fields=` "
        f"pour l'état client, `methods=` pour une surcharge de méthode. "
        f"Quinze composants recopiaient ce bloc, et deux en avaient "
        f"perdu un morceau."
    )


def test_the_detector_knows_the_real_shape() -> None:
    """Contrôle POSITIF, ancré sur la sortie réelle du primitive.

    Si la forme d'un scope changeait (espace après l'accolade, autre
    racine que ``$bz``), un littéral recopié depuis la sortie actuelle
    échapperait au détecteur — et l'interdiction resterait verte sans
    rien garder.
    """
    from bretzel.components.base._wiring import scope_literal

    real = scope_literal(
        "$bz.tabs.scope", cell="value", initial='"a"', server_synced=True,
    )
    pasted = "attrs['bz-data'] = \"" + real.replace('"', "'") + '"'
    assert hand_builds_a_scope(pasted), (
        f"le détecteur ne reconnaît plus la forme que produit "
        f"`scope_literal` ({real!r}) : la marque {_MARK!r} a changé."
    )
    bare = scope_literal("$bz.tabs.scope")
    assert _PURE_SPREAD.match(bare), (
        f"un scope sans rien d'autre que son étalement ({bare!r}) n'est "
        f"plus reconnu comme pur — la forme d'étalement a changé."
    )


def test_a_hand_built_scope_is_still_caught() -> None:
    """Les deux versants, sur des sources fabriquées : la forme fautive —
    un littéral qu'on complète — reste attrapée, l'étalement pur passe."""
    assert hand_builds_a_scope('attrs["bz-data"] = "{...$bz.x.scope, v: 1}"')
    assert hand_builds_a_scope('"{...$bz.x.scope," + body + "}"')
    # La marque hors de tout littéral d'une ligne : concaténation
    # multi-lignes, la forme qu'avaient `tabs` / `tree`.
    assert hand_builds_a_scope("parts = [\n  '{...$bz.x.scope'\n]")
    assert not hand_builds_a_scope('attrs["bz-data"] = "{...$bz.x.scope}"')
    assert not hand_builds_a_scope('scope_literal("$bz.x.scope", cell="value")')
    assert not hand_builds_a_scope("aucune marque ici")
