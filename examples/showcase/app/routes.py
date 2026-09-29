"""Mount every page under the shell.

The component pages are read from the catalogue: one entry there is one
route here, so the two cannot disagree. ``main`` rakes ``PAGES`` in via
``app.include``.
"""

import importlib

from bretzel import layout, page
from examples.showcase.app.catalog import CATALOG, module_name
from examples.showcase.app.layout import shell as shell_fn
from examples.showcase.features import home, studio

shell = layout(shell_fn)

PAGES = [
    page("/", layout=shell, title="Bretzel UI — components for Python web apps",
         description=home.SUMMARY)(home.page),
    page("/studio", layout=shell, title="Theme studio — Bretzel UI",
         description=studio.SUMMARY)(studio.page),
]

for _group, entries in CATALOG:
    for slug, label, _icon in entries:
        module = importlib.import_module(module_name(slug))
        PAGES.append(
            page(f"/{slug}", layout=shell, title=f"{label} — Bretzel UI",
                 description=module.SUMMARY)(module.page)
        )
