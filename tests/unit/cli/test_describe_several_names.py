"""``bretzel describe a b c`` : chaque fiche, dans l'ordre, en un appel.

Un nom inconnu ne cache pas les autres : son erreur part sur stderr et le
code de sortie vaut 2. En JSON, un seul nom garde l'objet d'avant ;
plusieurs donnent la liste de ces objets.
"""

from __future__ import annotations

import json

import pytest

from bretzel.cli.main import main


def test_each_card_in_order_and_an_unknown_name_hides_nothing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["describe", "ui.button", "nexistepas", "refreshable"]) == 2
    captured = capsys.readouterr()
    assert captured.out.index("ui.button → Button") < captured.out.index(
        "refreshable → bretzel"
    )
    assert "nexistepas" in captured.err and "nexistepas" not in captured.out


def test_json_keeps_one_object_for_one_name_and_lists_several(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cards = {}
    for name in ("page", "PageState"):
        assert main(["describe", name, "--json"]) == 0
        cards[name] = json.loads(capsys.readouterr().out)

    assert main(["describe", "page", "PageState", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == [cards["page"], cards["PageState"]]
