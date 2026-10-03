"""The board's identity: cool neutrals, one indigo accent, solid avatars.

This app is the public demo, so it wears a look of its own rather than
the framework's colourless default. The scale (control heights, text
steps) still comes from Bretzel: a theme names what the framework cannot
decide for an app, and nothing else.

- **The neutrals are cool**, a hair of blue in every grey, so the indigo
  reads as part of the surface rather than pasted on it.
- **Dark mode climbs in elevation**: page, then column, then card, each
  a step lighter. A card darker than the column it sits in reads as a
  hole.
- **The team's four hues are the app's own**, deep enough that all four
  derive WHITE initials on the board's solid avatars
  (``variant="solid"``). The palette's blue, orange and jade derive a
  dark foreground while its violet derives a white one, and four discs
  side by side in two ink colours read as a mistake.
- **Opening a card keeps the board in sight.** The shipped drawer dims
  the page to 50 % and blurs it, right for a modal task; here one opens
  a card to glance at it, and the board vanishing behind a blur at every
  click read as a disturbance. ⚠️ The backdrop slot is a copy of the
  shipped string with the dim lowered and the blur removed, so a later
  change to that slot will not reach this app.
"""

from bretzel.theme import Theme

THEME = Theme(
    semantic={
        "primary": "#5e6ad2",
        "background": "#f5f5f7",
        "surface": "#ffffff",
        "interface": "#eeeef2",
        "text": "#1b1c22",
        "muted": "#6b6e7a",
    },
    semantic_dark={
        "background": "#0d0e11",
        "surface": "#1b1c21",
        "interface": "#23242a",
        "text": "#e6e7eb",
        "muted": "#8b8e99",
    },
    palette={
        "berry": "#b4407e",
        "ocean": "#2f6fd6",
        "ember": "#c2410c",
        "pine": "#13836f",
    },
    shape={"box": "0.625rem", "field": "0.5rem", "selector": "0.375rem"},
    fonts={"sans": "Inter, 'Segoe UI Variable Text', 'Segoe UI', "
                   "system-ui, -apple-system, sans-serif"},
    components={
        "drawer": {
            "slots": {
                "backdrop": (
                    "fixed inset-0 z-40 bg-black/25 "
                    "transition-[opacity,visibility] duration-200 "
                    "data-[open=false]:opacity-0 data-[open=false]:invisible "
                    "data-[open=false]:pointer-events-none"
                ),
            },
        },
    },
)
