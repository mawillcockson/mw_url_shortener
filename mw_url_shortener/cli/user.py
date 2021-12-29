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


def get_by_id(id: int = typer.Argument(...)) -> None:
    if id < 0:
        typer.echo(f"'id' must be 0 or greater; got '{id}'")
        raise typer.Exit(code=1)

    user = inject.instance(UserInterface)
    resource = inject.instance(Resource)
    with open_resource(resource) as opened_resource:
        retrieved_user = run_sync(user.get_by_id(opened_resource, id=id))

    settings = inject.instance(Settings)
    if settings.output_style == OutputStyle.json:
        typer.echo(retrieved_user.json())
        return

    typer.echo(
        f"""id: {retrieved_user.id}
username: {retrieved_user.username}"""
    )


# update
# remove_by_id
# search

app = typer.Typer()
app.command()(create)
app.command()(get_by_id)
