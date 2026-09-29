"""TOPIC — Forms and their validation.

A Bretzel form is not a separate object: it is a ``ui.form`` around
ordinary fields, and the validation lives on the STATE, not on the view.

That is the point to grasp before all the rest. A `@validator` is
attached to a typed state field, so it applies whatever the write's
provenance — a form, a CSV import, a handler called by another. A
validation set on the view would only protect the path going through the
view.
"""

from __future__ import annotations

from bretzel import page, ui
from examples.docs.features.shell import shell

PATH = "/forms"


@page(PATH, layout=shell, title="Forms")
def forms_page() -> None:
    with ui.container(width="xl"):
        with ui.vstack(gap="lg"):
            ui.heading('Forms', level=1, size="3xl")
            ui.text(
                'Fields, a `ui.form` around them, and the validation on '
                'the STATE — not on the view. That last point is what '
                'makes the difference between “the form refuses” and “the '
                'data cannot be wrong”.',
                color="muted", size="lg",
            )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('The skeleton', level=2)
                    ui.text(
                        '`ui.form` is a container: its children are '
                        'written inside a `with`. `on_submit=` receives '
                        "the form's values.",
                        color="muted", size="sm",
                    )
                    ui.code(
                        'def register(name: str, email: str) -> None:\n    Account().create(name=name, email=email)\n\nwith ui.form(on_submit=register):\n    with ui.form_field(label="Name", required=True):\n        ui.input(name="name")\n    with ui.form_field(label="Email",\n                       hint="A work address, preferably"):\n        ui.input(name="email", type="email")\n    ui.button("Create", type="submit", color="primary")\n',
                        lang="python",
                    )
                    ui.text(
                        '`ui.form_field` carries the label above, the '
                        'field in the middle, the hint or the error '
                        'underneath. It also sets the accessibility links '
                        '— a screen reader announces the error with the '
                        'field, without anyone writing it.',
                        color="muted", size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Validation lives on the STATE', level=2)
                    ui.text(
                        'A `@validator` attaches to a typed state field. '
                        'It runs on EVERY assignment — so from the form as'
                        ' much as from an import, a handler, a script.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        'from bretzel.state import SessionState, field, validator\n\nclass Signup(SessionState):\n    email: str = field(default="")\n    age: int = field(default=0)\n\n    @validator("email")\n    def _valid_email(self, value: str) -> str:\n        """A FIELD validator: it receives the value and\n        returns the one we keep — so it can normalise\n        too."""\n        value = value.strip().lower()\n        if "@" not in value:\n            raise ValueError("Invalid address.")\n        return value\n\n    @validator\n    def _consistent(self) -> None:\n        """An INSTANCE validator: it runs after any\n        mutation, and sees every field."""\n        if self.age < 18 and self.email.endswith(".pro"):\n            raise FormError("Business account: 18 minimum.")\n',
                        lang="python",
                    )
                    ui.table(
                        columns=[
                            ui.column("forme", label="Form"),
                            ui.column("quand", label="When it runs"),
                            ui.column("recoit", label='What it receives'),
                        ],
                        rows=[
                            {"forme": "@validator(\"field\")",
                             "quand": 'on every assignment to THIS field',
                             "recoit": '`(self, value)` — and returns the '
                                       'value to keep'},
                            {"forme": "@validator",
                             "quand": 'after any mutation of the instance',
                             "recoit": '`(self)` — it sees every field, '
                                       'and raises to refuse'},
                        ],
                        size="sm",
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading("Showing the error", level=2)
                    ui.text(
                        '`ui.form_field(error=…)` shows the message under '
                        'the field AND sets `aria-invalid` — the two go '
                        'together, otherwise the error exists on screen '
                        'and not for a screen reader.',
                        color="muted", size="sm",
                    )
                    ui.code(
                        "signup = Signup()\n"
                        "with ui.form_field(label=\"Email\",\n"
                        "                   error=signup.errors.get(\"email\")):\n"
                        "    ui.input(name=\"email\", value=signup.email)\n",
                        lang="python",
                    )
                    ui.alert(
                        '`FormError` is the raise meant to TRAVEL BACK to '
                        'the form — that is what distinguishes it from a '
                        'bare `ValueError`, which says “this value is '
                        'impossible” and comes back as a server error.',
                        color="info", title='Two ways of refusing',
                    )

            with ui.card():
                with ui.vstack(gap="sm"):
                    ui.heading('Why not on the view', level=2)
                    ui.text(
                        'Because an app has several write routes and one '
                        'form. A CSV import, a handler called from another'
                        ' page, a data migration: all write into the same '
                        'state, none goes through the view. A rule placed '
                        'on the field covers them all; a rule placed on '
                        'the form covers one.',
                        color="muted", size="sm",
                    )

            with ui.card(color="surface"):
                with ui.hstack(gap="sm", wrap=True, align="baseline"):
                    ui.text('Typed state, its four scopes, and the fields:', color="muted", size="sm")
                    ui.link('Server state →', href="/state-server")
                    ui.link("Server actions →", href="/actions-server")
