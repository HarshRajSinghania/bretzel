"""Showcase entry point — run with ``py -m examples.showcase.main``.

The public face of the component library: one page per component, each
with a few real uses and their code, and a theme studio that repaints
the whole app. Every page is painted by the same client store, so an
identity picked in the top bar follows you everywhere.
"""

import os
from html import escape

from fastapi import Response

from bretzel import Bretzel
from examples.showcase.app import routes
from examples.showcase.features import errors

#: A local run stays in dev with a throwaway key. The public site sets
#: ``BRETZEL_MODE=prod``: the key then comes from ``$BRETZEL_SECRET_KEY``
#: (``secret_key=None`` falls through to it), and the framework refuses to
#: start without one.
MODE = os.environ.get("BRETZEL_MODE", "dev")

app = Bretzel(
    title="Bretzel UI",
    description="Every Bretzel component, in real uses, under the theme you pick.",
    secret_key="dev-showcase-secret-change-me" if MODE == "dev" else None,
    mode=MODE,
)


app.include(routes.PAGES, errors)

#: Where the public site lives — what the sitemap announces.
SITE = "https://ui.bretzel-py.dev"


@app.fastapi.get("/robots.txt", include_in_schema=False)
async def robots_txt() -> Response:
    return Response(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
                    media_type="text/plain")


@app.fastapi.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml() -> Response:
    """Every page, read from the MOUNTED routes: a page added to the
    catalogue is announced without touching this function. The
    framework's own endpoints (``/_…``) and these two files are not pages."""
    paths = sorted({
        route.path for route in app.fastapi.routes
        if getattr(route, "path", "").startswith("/")
        and not route.path.startswith("/_") and "{" not in route.path
        and route.path not in {"/robots.txt", "/sitemap.xml"}
    })
    entries = "".join(f"  <url><loc>{SITE}{escape(path)}</loc></url>\n"
                      for path in paths)
    return Response('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                    f"{entries}</urlset>\n", media_type="application/xml")


if __name__ == "__main__":
    app.run(port=8020, reload=True)
