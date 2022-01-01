# mypy: allow_any_expr
"the 'user' subcommand of the client"
import json
from typing import Optional

import typer
from pydantic.json import pydantic_encoder

from mw_url_shortener.dependency_injection import get_settings
from mw_url_shortener.interfaces import (
    RedirectInterface,
    get_redirect_interface,
    get_resource,
    open_resource,
    run_sync,
)
from mw_url_shortener.schemas.redirect import RedirectCreate, RedirectUpdate
from mw_url_shortener.settings import OutputStyle, Settings, defaults


def create(
    url: str = typer.Argument(...),
    short_link: str = typer.Argument(...),
    response_status: int = typer.Option(
        defaults.redirect_response_status,
        help="HTTP code to respond with (see https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)",
    ),
    body: Optional[str] = typer.Option(defaults.redirect_body),
) -> None:
    redirect_create_schema = RedirectCreate(
        url=url, short_link=short_link, response_status=response_status, body=body
    )

    redirect = get_redirect_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        created_redirect = run_sync(
            redirect.create(
                opened_resource, create_object_schema=redirect_create_schema
            )
        )

    settings = get_settings()
    if settings.output_style == OutputStyle.json:
        typer.echo(created_redirect.json())
        return

    typer.echo(
        f"""successfully created redirect
id: {created_redirect.id}
url: {created_redirect.url}
short link: {created_redirect.short_link}
response_status: {created_redirect.response_status}
body: {created_redirect.body}"""
    )


def get_by_id(id: int = typer.Argument(...)) -> None:
    if id < 0:
        typer.echo(f"'id' must be 0 or greater; got '{id}'")
        raise typer.Exit(code=1)

    redirect = get_redirect_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        retrieved_redirect = run_sync(redirect.get_by_id(opened_resource, id=id))

    settings = get_settings()

    if retrieved_redirect is None and settings.output_style == OutputStyle.text:
        typer.echo(f"could not find redirect with id '{id}'")

    if retrieved_redirect is None:
        raise typer.Exit(code=1)

    if settings.output_style == OutputStyle.json:
        typer.echo(retrieved_redirect.json())
        return

    typer.echo(
        f"""id: {retrieved_redirect.id}
url: {created_redirect.url}
short link: {created_redirect.short_link}
response_status: {created_redirect.response_status}
body: {created_redirect.body}"""
    )


def search(
    skip: int = typer.Option(0, help="how many results to skip over (default 0)"),
    limit: int = typer.Option(
        100, help="how many results to show at once (default 100)"
    ),
    url: Optional[str] = typer.Option(None),
    short_link: Optional[str] = typer.Option(None),
    response_status: Optional[str] = typer.Option(None),
    body: Optional[str] = typer.Option(None),
) -> None:
    redirect = get_redirect_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        retrieved_redirects = run_sync(
            redirect.search(
                opened_resource,
                skip=skip,
                limit=limit,
                url=url,
                short_link=short_link,
                response_status=response_status,
                body=body,
            )
        )

    settings = get_settings()
    if settings.output_style == OutputStyle.json:
        # NOTE:FUTURE partial serialization would allow for serializing
        # pydantic.BaseModels into an object that json.dumps can encode, and
        # can thus be included in other arbitrary data, like a list
        # https://github.com/samuelcolvin/pydantic/issues/951
        typer.echo(json.dumps(retrieved_redirects, default=pydantic_encoder))
        return

    for retrieved_redirect in retrieved_redirects:
        typer.echo(
            f"""id: {retrieved_redirect.id}
url: {created_redirect.url}
short link: {created_redirect.short_link}
response_status: {created_redirect.response_status}
body: {created_redirect.body}
"""  # extra newline for separation
        )


def remove_by_id(id: int = typer.Argument(...)) -> None:
    if id < 0:
        typer.echo(f"'id' must be 0 or greater; got '{id}'")
        raise typer.Exit(code=1)

    redirect = get_redirect_interface()
    resource = get_resource()
    with open_resource(resource) as opened_resource:
        removed_redirect = run_sync(redirect.remove_by_id(opened_resource, id=id))

    settings = get_settings()
    if settings.output_style == OutputStyle.json:
        typer.echo(removed_redirect.json())
        return

    typer.echo(
        f"""successfully removed redirect
id: {removed_redirect.id}
url: {created_redirect.url}
short link: {created_redirect.short_link}
response_status: {created_redirect.response_status}"""
    )


app = typer.Typer()
app.command()(create)
app.command()(get_by_id)
app.command()(search)
app.command()(remove_by_id)
