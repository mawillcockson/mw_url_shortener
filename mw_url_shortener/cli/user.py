"the 'user' subcommand of the client"
import json
from typing import Optional

import inject
import typer
from pydantic.json import pydantic_encoder

from mw_url_shortener.interfaces import (
    UserInterface,
    get_resource,
    open_resource,
    run_sync,
)
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
    resource = get_resource()
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
    resource = get_resource()
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


def search(
    skip: int = typer.Option(0, help="how many results to skip over (default 0)"),
    limit: int = typer.Option(
        100, help="how many results to show at once (default 100)"
    ),
    username: Optional[str] = typer.Option(None),
) -> None:
    user = inject.instance(UserInterface)
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        retrieved_users = run_sync(
            user.search(opened_resource, skip=skip, limit=limit, username=username)
        )

    settings = inject.instance(Settings)
    if settings.output_style == OutputStyle.json:
        # NOTE:FUTURE partial serialization would allow for serializing
        # pydantic.BaseModels into an object that json.dumps can encode, and
        # can thus be included in other arbitrary data, like a list
        # https://github.com/samuelcolvin/pydantic/issues/951
        typer.echo(json.dumps(retrieved_users, default=pydantic_encoder))
        return

    for retrieved_user in retrieved_users:
        typer.echo(
            f"""id: {retrieved_user.id}
username: {retrieved_user.username}
"""  # extra newline for separation
        )


# update
# remove_by_id

app = typer.Typer()
app.command()(create)
app.command()(get_by_id)
app.command()(search)
