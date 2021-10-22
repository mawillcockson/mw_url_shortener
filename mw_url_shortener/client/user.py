"the 'user' subcommand of the client"
import typer

from ..settings import CommonSettings

app = typer.Typer()


@app.command()
def create(
    ctx: typer.Context,
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    ctx.ensure_object(CommonSettings)
    typer.echo(f"the database url is: '{ctx.obj.database_url}'")
    typer.echo(f"username is '{username}'")
    typer.echo(f"password is '{password}'")
