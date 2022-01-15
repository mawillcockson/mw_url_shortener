from typing import TYPE_CHECKING, cast

import inject

from mw_url_shortener.interfaces.base import Resource
from mw_url_shortener.interfaces.user_interface import UserInterface
from mw_url_shortener.interfaces.redirect_interface import RedirectInterface
from mw_url_shortener.settings import CliMode

from .settings import get_settings

if TYPE_CHECKING:
    from typing import Optional, Sequence, Type

    from httpx import AsyncClient

    from mw_url_shortener.database.start import AsyncSession, sessionmaker
    from mw_url_shortener.interfaces.base import (
        ContravariantCreateSchemaType,
        ContravariantOpenedResourceT,
        ContravariantUpdateSchemaType,
        InterfaceBaseProtocol,
        ObjectSchemaType,
        ResourceT,
    )


def get_resource(resource_type: "Optional[Type[ResourceT]]" = None) -> "ResourceT":
    if resource_type is None:
        settings = get_settings()
        if settings.cli_mode == CliMode.local_database:
            return cast("ResourceT", inject.instance("sessionmaker[AsyncSession]"))
        return cast("ResourceT", inject.instance("AsyncClient"))

    return inject.instance(resource_type)


def inject_resource(binder: "inject.Binder", *, resource: "ResourceT") -> None:
    binder.bind(Resource, resource)


def inject_interface(
    binder: "inject.Binder",
    *,
    interface_type: """Type[
        InterfaceBaseProtocol[
            ContravariantOpenedResourceT,
            ObjectSchemaType,
            ContravariantCreateSchemaType,
            ContravariantUpdateSchemaType,
        ]
    ]""",
    interface: """InterfaceBaseProtocol[
        ContravariantOpenedResourceT,
        ObjectSchemaType,
        ContravariantCreateSchemaType,
        ContravariantUpdateSchemaType,
    ]""",
) -> None:
    binder.bind(interface_type, interface)


def get_user_interface(
    interface_type: "Optional[Type[UserInterface[ContravariantOpenedResourceT]]]" = None,
) -> "UserInterface[ContravariantOpenedResourceT]":
    if interface_type is None:
        user_interface = inject.instance(UserInterface)
    else:
        user_interface = inject.instance(interface_type)

    assert isinstance(
        user_interface, UserInterface
    ), f"{user_interface} is not UserInterface"
    return user_interface


def get_redirect_interface(
    interface_type: "Optional[Type[RedirectInterface[ContravariantOpenedResourceT]]]" = None,
) -> "RedirectInterface[ContravariantOpenedResourceT]":
    if interface_type is None:
        redirect_interface = inject.instance(RedirectInterface)
    else:
        redirect_interface = inject.instance(interface_type)

    assert isinstance(
        redirect_interface, RedirectInterface
    ), f"{redirect_interface} is not RedirectInterface"
    return redirect_interface
