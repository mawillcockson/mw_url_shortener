from httpx import AsyncClient

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces import (
    OpenedResourceT,
    RedirectInterface,
    UserInterface,
)
from mw_url_shortener.interfaces import database as database_interface


def test_user_interface() -> None:
    assert isinstance(database_interface.user, UserInterface)

    # for mypy
    def use_user_generic(user: UserInterface[OpenedResourceT]) -> None:
        pass

    use_user_generic(database_interface.user)

    def use_user_asyncsession(user: UserInterface[AsyncSession]) -> None:
        pass

    use_user_asyncsession(database_interface.user)

    def use_user_asyncclient(user: UserInterface[AsyncClient]) -> None:
        pass

    # use_user_asyncclient(http_interface.user)


def test_redirect_interface() -> None:
    assert isinstance(database_interface.redirect, RedirectInterface)

    # for mypy
    def use_redirect_generic(redirect: RedirectInterface[OpenedResourceT]) -> None:
        pass

    use_redirect_generic(database_interface.redirect)

    def use_redirect_asyncsession(redirect: RedirectInterface[AsyncSession]) -> None:
        pass

    use_redirect_asyncsession(database_interface.redirect)

    def use_redirect_asyncclient(redirect: RedirectInterface[AsyncClient]) -> None:
        pass

    # use_redirect_asyncclient(http_interface.redirect)


def do_not_run() -> None:
    "for mypy"
    # reveal_type(database_interface.user.get_by_id)
    # reveal_type(UserInterface.get_by_id)
    # reveal_type(database_interface.user.update)
    # reveal_type(UserInterface.update)

    # reveal_type(database_interface.redirect.get_by_id)
    # reveal_type(RedirectInterface.get_by_id)
    # reveal_type(database_interface.redirect.update)
    # reveal_type(RedirectInterface.update)
