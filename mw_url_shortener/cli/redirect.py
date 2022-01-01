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


app = typer.Typer()
app.command()(create)
