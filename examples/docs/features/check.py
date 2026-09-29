"""GETTING STARTED — Judging the code written against the framework.

"Describe the UI"'s twin: ``describe`` SAYS what exists, ``check``
judges what was done with it. The twelve rules are read live from
:data:`bretzel.lint.rules.STATIC` — their name and their sentence come
from the module carrying them, so this chapter cannot announce a dead
rule nor keep quiet about a new one.

⚠️ This page imports ``bretzel.lint``, which no module of the framework
is allowed to do (the ``lint-stays-extractable`` contract). It is
deliberate and has no effect on the guarantee: ``examples/docs`` is an
APP, not the framework — if ``lint`` ever left the repository, this
chapter would leave with it, which is exactly the intended behaviour.
"""

from __future__ import annotations

from bretzel import page, ui
from bretzel.lint import rule_summaries

from examples.docs.features.shell import shell

PATH = "/check"


def rule_rows() -> list[dict[str, str]]:
    """The live rules and their sentence, through the linter's public
    door.

    ``rule_summaries()`` IS what the CLI runs, and the sentence comes
    from the module carrying the rule: a rule added appears here at the
    next render, a rule removed disappears, and no line of this page
    repeats what is written elsewhere. A catalogue copied by hand drifts
    faster than it serves — this repository deleted a whole skill for
    that reason.
    """
    return [
        {"regle": slug, "refuse": phrase}
        for slug, phrase in rule_summaries().items()
    ]


@page(PATH, layout=shell, title='Judge the code')
def check_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading('Judge the code', level=1, size="3xl")
            ui.text(
                '`describe` says what exists; `check` judges what you made'
                ' of it. Both read the INSTALLED code, so neither can be '
                'out of date.',
                color="muted", size="lg",
            )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Running it', level=2)
                    ui.code(
                        "py -m bretzel.cli.main check my_app/\n"
                        "py -m bretzel.cli.main check --deep my_app.main:app\n",
                        lang="bash",
                    )
                    ui.text(
                        'The first pass is STATIC: it reads the files, '
                        'mounts nothing, and needs no app to start. '
                        '`--deep` additionally mounts the real app and '
                        'arbitrates its map — the declared features '
                        'against what they really do.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Why ONE MORE linter', level=2)
                    ui.text(
                        'Ruff and mypy judge Python. Neither knows that an'
                        ' unknown kwarg passed to `ui.button` leaves as an'
                        ' inert HTML attribute: it does not raise, it does'
                        ' not show, and it is not visible in review. That '
                        'is the dominant failure mode here, and it is the '
                        'one these rules take — each catches a SILENT '
                        'mistake.',
                        color="muted", size="sm",
                    )

            with ui.card(color="surface"):
                with ui.vstack(gap="md"):
                    rows = rule_rows()
                    with ui.hstack(align="center", gap="sm"):
                        ui.heading("What it can see", level=2)
                        ui.badge(str(len(rows)), color="muted",
                                 variant="outline")
                    ui.text(
                        'Read live by `rule_summaries()` — the table the '
                        'CLI executes, and the sentence every rule carries'
                        ' at the head of its module. A new rule appears '
                        'here without this page being edited.',
                        color="muted", size="sm",
                    )
                    ui.table(
                        columns=[
                            ui.column("regle", label='Rule'),
                            ui.column("refuse", label="It refuses…"),
                        ],
                        rows=rows,
                        size="sm",
                    )
