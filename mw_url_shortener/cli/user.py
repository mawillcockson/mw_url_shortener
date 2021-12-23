"the 'user' subcommand of the client"
import inject
import typer

from mw_url_shortener.settings import Settings

app = typer.Typer()


@app.command()
def create(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
) -> None:
    settings = inject.instance(Settings)
    typer.echo(f"settings are\n{settings}")
    typer.echo(f"the database url is: '{ctx.obj.database_url}'")
    typer.echo(f"username is '{username}'")
    typer.echo(f"password is '{password}'")

    # should instead use python-inject in the database_interface to provide
    # AsyncSession, and pass the async_session_awaitable as the first task to
    # run in a queue, and then the awaitable that performs the user creation as
    # the second task
    async def wrapper(async_session_awaitable: "Awaitable[AsyncSession]", func) -> None:
        async_session = await async_session_awaitable
        return await func(async_session_awaitable)


# update
# remove_by_id
# search
