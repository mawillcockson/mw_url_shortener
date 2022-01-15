# mypy: allow_any_expr
"the 'user' subcommand of the client"
import json
from typing import Optional

import typer
from pydantic.json import pydantic_encoder

from mw_url_shortener.dependency_injection import (
    get_resource,
    get_settings,
    get_user_interface,
)
from mw_url_shortener.interfaces import UserInterface, open_resource, run_sync
from mw_url_shortener.schemas.user import UserCreate, UserUpdate
from mw_url_shortener.settings import OutputStyle, Settings


def create(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    create_user_schema = UserCreate(username=username, password=password)

    user = get_user_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        created_user = run_sync(
            user.create(opened_resource, create_object_schema=create_user_schema)
        )

    settings = get_settings()
    if created_user is None and settings.output_style == OutputStyle.text:
        typer.echo(
            f"""couldn't create user with
username: '{username}'
password: '{password}'"""
        )

    if created_user is None:
        raise typer.Exit(code=1)

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

    user = get_user_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        retrieved_user = run_sync(user.get_by_id(opened_resource, id=id))

    settings = get_settings()

    if retrieved_user is None and settings.output_style == OutputStyle.text:
        typer.echo(f"could not find user with id '{id}'")
    if retrieved_user is None:
        raise typer.Exit(code=1)

    if settings.output_style == OutputStyle.json:
        typer.echo(retrieved_user.json())
        return

    typer.echo(
        f"""id: {retrieved_user.id}
username: {retrieved_user.username}"""
    )


def search(
    skip: int = typer.Option(0, help="how many results to skip over"),
    limit: int = typer.Option(100, help="how many results to show at once"),
    username: Optional[str] = typer.Option(None),
) -> None:
    user = get_user_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        retrieved_users = run_sync(
            user.search(opened_resource, skip=skip, limit=limit, username=username)
        )

    settings = get_settings()
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


def remove_by_id(id: int = typer.Argument(...)) -> None:
    if id < 0:
        typer.echo(f"'id' must be 0 or greater; got '{id}'")
        raise typer.Exit(code=1)

    user = get_user_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        removed_user = run_sync(user.remove_by_id(opened_resource, id=id))

    settings = get_settings()

    if removed_user is None and settings.output_style == OutputStyle.text:
        typer.echo(f"could not find user with id '{id}'")
    if removed_user is None:
        raise typer.Exit(code=1)

    if settings.output_style == OutputStyle.json:
        typer.echo(removed_user.json())
        return

    typer.echo(
        f"""successfully removed user
id: {removed_user.id}
username: {removed_user.username}"""
    )


def check_authentication(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
) -> None:
    "check if username and password are valid"
    user = get_user_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        valid_user = run_sync(
            user.authenticate(opened_resource, username=username, password=password)
        )

    settings = get_settings()

    if valid_user is None and settings.output_style == OutputStyle.text:
        typer.echo("invalid username/password combination")

    if valid_user is None:
        raise typer.Exit(code=1)

    if settings.output_style == OutputStyle.json:
        typer.echo(valid_user.json())
        return

    typer.echo(
        f"""authentication successful
id: {valid_user.id}
username: {valid_user.username}"""
    )


def update_by_id(
    id: int = typer.Argument(...),
    username: Optional[str] = typer.Option(None),
    # NOTE:FUTURE allow the password option to be passed without a value, which
    # will prompt for input
    # Would likely require either subclassing typer.Option or click.ParamType:
    # https://github.com/tiangolo/typer/issues/311
    password: Optional[str] = typer.Option(None),
) -> None:
    # validate first
    user_update_schema = UserUpdate(username=username, password=password)

    # then check if the user exists
    user = get_user_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        old_user = run_sync(user.get_by_id(opened_resource, id=id))

    settings = get_settings()

    if old_user is None and settings.output_style == OutputStyle.text:
        typer.echo(f"could not find user with id '{id}'")
    if old_user is None:
        raise typer.Exit(code=1)

    with open_resource(resource) as opened_resource:
        updated_user = run_sync(
            user.update(
                opened_resource,
                current_object_schema=old_user,
                update_object_schema=user_update_schema,
            )
        )

    assert updated_user, f"user existed before update, but not after: {old_user}"

    if settings.output_style == OutputStyle.json:
        typer.echo(updated_user.json())
        return

    typer.echo(f"successfully updated user\nid: {updated_user.id}")
    typer.echo(f"username: {updated_user.username}", nl=False)
    if old_user.username != updated_user.username:
        typer.echo(f" -> {updated_user.username}", nl=False)
    typer.echo("")


app = typer.Typer()
app.command()(create)
app.command()(get_by_id)
app.command()(search)
app.command()(remove_by_id)
app.command()(check_authentication)
app.command()(update_by_id)
