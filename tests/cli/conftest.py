import asyncio
from functools import partial, wraps
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable, Iterator, List, Protocol
from unittest.mock import patch

import inject
import pytest
from click.testing import Result
from pytest import CaptureFixture
from typer import Typer
from typer.testing import CliRunner

from mw_url_shortener.dependency_injection import (
    initialize_dependency_injection,
    reconfigure_dependency_injection,
)
from mw_url_shortener.remote.start import make_async_client
from mw_url_shortener.server.settings import ServerSettings, inject_server_settings
from mw_url_shortener.settings import OutputStyle
from tests.server.conftest import *  # need these fixtures

if TYPE_CHECKING:
    from asyncio import BaseEventLoop as AsyncLoopType
    from typing import Optional

    from _pytest.fixtures import SubRequest
    from fastapi.testclient import TestClient
    from httpx import AsyncClient
    from starlette.testclient import ASGI3App

    from mw_url_shortener.interfaces.base import OpenedResourceT, ResourceT
    from mw_url_shortener.interfaces.redirect_interface import RedirectInterface
    from mw_url_shortener.interfaces.user_interface import UserInterface
    from mw_url_shortener.schemas.security import AuthorizationHeaders
    from mw_url_shortener.schemas.user import Password, User, Username
    from mw_url_shortener.settings import Settings


@pytest.fixture
def cli_test_client() -> Iterator[CliRunner]:
    inject.clear()
    try:
        yield CliRunner()
    finally:
        inject.clear()


def patch_make_async_client(
    server_app: "ASGI3App",
) -> "Callable[[Settings, Username, Password], AsyncClient]":
    @wraps(make_async_client)
    def set_transport(
        settings: "Settings", username: "Username", password: "Password"
    ) -> "AsyncClient":
        import httpx

        async_client = make_async_client(
            settings=settings, username=username, password=password
        )
        async_client._transport = httpx.ASGITransport(server_app)

        return async_client

    return set_transport


class ReconfigureDependencyInjectionCommand(Protocol):
    "from: https://stackoverflow.com/a/68392079"

    def __call__(
        self,
        resource: "ResourceT",
        user_interface: "UserInterface[OpenedResourceT]",
        redirect_interface: "RedirectInterface[OpenedResourceT]",
        settings: "Optional[Settings]" = None,
        loop: "Optional[AsyncLoopType]" = None,
        configurators: "Optional[List[inject.BinderCallable]]" = None,
    ) -> None:
        raise NotImplementedError


def patch_reconfigure_dependency_injection(
    server_settings: "ServerSettings",
) -> ReconfigureDependencyInjectionCommand:
    server_settings_injector = partial(
        inject_server_settings, server_settings=server_settings
    )

    @wraps(reconfigure_dependency_injection)
    def reconfigure_er(
        resource: "ResourceT",
        user_interface: "UserInterface[OpenedResourceT]",
        redirect_interface: "RedirectInterface[OpenedResourceT]",
        settings: "Optional[Settings]" = None,
        loop: "Optional[AsyncLoopType]" = None,
        configurators: "Optional[List[inject.BinderCallable]]" = None,
    ) -> None:
        if configurators is None:
            configurators = [server_settings_injector]
        else:
            configurators.append(server_settings_injector)

        reconfigure_dependency_injection(
            resource=resource,
            user_interface=user_interface,
            redirect_interface=redirect_interface,
            settings=settings,
            loop=loop,
            configurators=configurators,
        )

    return reconfigure_er


class CommandRunner(Protocol):
    "from: https://stackoverflow.com/a/68392079"

    def __call__(
        self,
        app: Typer,
        arguments: List[str],
        clear_injection: bool = True,
        add_default_parameters: bool = True,
        /,
    ) -> Awaitable[Result]:
        raise NotImplementedError


# explained in docs/async_architecture.md
@pytest.fixture(
    params=[
        pytest.param("local", marks=pytest.mark.local),
        pytest.param("remote", marks=pytest.mark.remote),
    ],
    ids=["local", "remote"],
)
async def run_test_command(
    request: "SubRequest",
    capsys: CaptureFixture[str],
    cli_test_client: CliRunner,
    anyio_backend: str,
    on_disk_database: Path,
    test_client: "TestClient",
    test_user: "User",
    test_password: str,
    authorization_headers: "AuthorizationHeaders",
) -> CommandRunner:
    patched_make_async_client = patch_make_async_client(test_client.app)

    server_settings = inject.instance(ServerSettings)
    patched_reconfigure_dependency_injection = patch_reconfigure_dependency_injection(
        server_settings
    )

    # The test_client fixture called make_fastapi_app() which injected
    # ServerSettings. Now that we've captured it, we can clear dependency
    # injection and let the patched reconfigure_er re-inject it from inside the
    # cli app
    inject.clear()

    async def runner(
        app: Typer,
        arguments: List[str],
        clear_injection: bool = True,
        add_default_parameters: bool = True,
    ) -> Result:
        if add_default_parameters and request.param == "local":
            all_arguments = [
                "--output-style",
                OutputStyle.json.value,
                "local",
                "--database-path",
                str(on_disk_database),
            ]
            all_arguments.extend(arguments)
        elif add_default_parameters and request.param == "remote":
            all_arguments = [
                "--output-style",
                OutputStyle.json.value,
                "remote",
                "--base-url",
                "http://does-not-matter",
                "--username",
                str(test_user.username),
                "--password",
                test_password,
            ]
            all_arguments.extend(arguments)
        else:
            all_arguments = arguments
        test_command = partial(cli_test_client.invoke, app, all_arguments)

        remote_reconfigure_patcher = patch(
            "mw_url_shortener.cli.remote_subcommand.reconfigure_dependency_injection",
            new=patched_reconfigure_dependency_injection,
        )
        remote_make_async_client_patcher = patch(
            "mw_url_shortener.cli.remote_subcommand.make_async_client",
            new=patched_make_async_client,
        )
        local_reconfigure_patcher = patch(
            "mw_url_shortener.cli.local_subcommand.reconfigure_dependency_injection",
            new=patched_reconfigure_dependency_injection,
        )

        try:
            initialize_dependency_injection()

            remote_reconfigure_patcher.start()
            remote_make_async_client_patcher.start()
            local_reconfigure_patcher.start()

            with capsys.disabled():
                result = await asyncio.get_running_loop().run_in_executor(
                    None, test_command
                )

            return result

        finally:
            remote_reconfigure_patcher.stop()
            remote_make_async_client_patcher.stop()
            local_reconfigure_patcher.stop()

            if clear_injection:
                inject.clear()

    return runner
