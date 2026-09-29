"""``ui.icon_button(href=…)`` is a link, as ``ui.button(href=…)`` is one."""

from __future__ import annotations


class TestAnIconButtonCanBeALink:
    """``href=`` makes it an ``<a>``, as it makes ``ui.button`` one — it
    used to land on a ``<button>``, where it did nothing."""

    def test_href_renders_an_anchor(self) -> None:
        from bretzel.components.actions.icon_button import IconButton
        from bretzel.components.base.testing import render_isolated
        from bretzel.core.serialize import serialize

        with render_isolated():
            html = serialize(IconButton("github", href="https://x.dev",
                                        external=True, aria_label="Source").render())
        assert html.startswith("<a ") and 'href="https://x.dev"' in html
        assert 'target="_blank"' in html and 'rel="noopener noreferrer"' in html
        assert 'type="button"' not in html

    def test_href_and_on_click_are_refused_together(self) -> None:
        import pytest

        from bretzel.components.actions.icon_button import IconButton
        from bretzel.components.base.testing import render_isolated

        with render_isolated(), pytest.raises(TypeError, match="href"):
            IconButton("x", href="/a", on_click="x = 1")
