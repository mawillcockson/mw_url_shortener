"the 'user' subcommand of the client"
import inject
import typer

from mw_url_shortener.interfaces import Resource, UserInterface, open_resource, run_sync
from mw_url_shortener.schemas.user import UserCreate
from mw_url_shortener.settings import OutputStyle, Settings


def create(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    create_user_schema = UserCreate(username=username, password=password)

    user = inject.instance(UserInterface)
    resource = inject.instance(Resource)
    with open_resource(resource) as opened_resource:
        created_user = run_sync(
            user.create(opened_resource, create_object_schema=create_user_schema)
        )

    settings = inject.instance(Settings)
    if settings.output_style == OutputStyle.json:
        typer.echo(created_user.json())
        return

    typer.echo(
        f"""successfully created user
id: {created_user.id}
username: {created_user.username}"""
    )


# update
# remove_by_id
# search

app = typer.Typer()
app.command()(create)
