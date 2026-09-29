"""``bretzel check`` lit le code de l'app, pas ce qui dort à côté.

Mesuré le 2026-09-27 : un ``bretzel check .`` à la racine de ce dépôt
lisait 9 902 fichiers, dont 7 479 sous ``.claude/worktrees`` et
``.bretzel`` — 5 min 28 s pour ~1 500 fichiers de vrai code. La
découverte ne sautait que dix noms écrits en dur, et les comparait à
TOUT le chemin : un projet rangé sous ``~/build/`` n'était jamais lu.
"""

from __future__ import annotations

from pathlib import Path

from bretzel.lint.corpus import discover


def tree(root: Path, *relative: str) -> None:
    for rel in relative:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x = 1\n", encoding="utf-8")


def found(root: Path, entry: Path) -> list[str]:
    return [p.relative_to(root).as_posix() for p in discover([entry])]


def test_hidden_and_tool_folders_are_skipped(tmp_path: Path) -> None:
    tree(
        tmp_path,
        "main.py",
        "features/home.py",
        ".claude/worktrees/copy/main.py",
        ".venv/lib/site.py",
        "env/pyvenv.cfg",
        "env/lib/site-packages/pkg.py",
        "features/.cache/old.py",
        "node_modules/pkg/x.py",
        "__pycache__/main.py",
    )
    assert found(tmp_path, tmp_path) == ["features/home.py", "main.py"]


def test_a_folder_named_explicitly_is_read(tmp_path: Path) -> None:
    """Le versant LICITE : la règle vaut pour ce qui est SOUS le chemin
    donné, jamais pour le chemin lui-même."""
    tree(tmp_path, ".claude/tool/run.py", "build/app/main.py")
    assert found(tmp_path, tmp_path / ".claude" / "tool") == [".claude/tool/run.py"]
    assert found(tmp_path, tmp_path / "build" / "app") == ["build/app/main.py"]


def test_the_order_is_stable(tmp_path: Path) -> None:
    """Trié comme avant : un rapport ne change pas d'ordre d'un système
    de fichiers à l'autre."""
    tree(tmp_path, "b.py", "a/z.py", "a/b.py", "c/a.py")
    assert found(tmp_path, tmp_path) == ["a/b.py", "a/z.py", "b.py", "c/a.py"]
