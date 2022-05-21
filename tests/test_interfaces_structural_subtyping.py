from httpx import AsyncClient

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces import (
    LogInterface,
    OpenedResourceT,
    RedirectInterface,
    UserInterface,
)
from mw_url_shortener.interfaces import database as database_interface
from mw_url_shortener.interfaces import remote as remote_interface


def test_user_interface() -> None:
    assert isinstance(database_interface.user, UserInterface)
    assert isinstance(remote_interface.user, UserInterface)

    # for mypy
    def use_user_generic(user: UserInterface[OpenedResourceT]) -> None:
        pass

    use_user_generic(database_interface.user)
    use_user_generic(remote_interface.user)

    def use_user_asyncsession(user: UserInterface[AsyncSession]) -> None:
        pass

    use_user_asyncsession(database_interface.user)

    def use_user_asyncclient(user: UserInterface[AsyncClient]) -> None:
        pass

    use_user_asyncclient(remote_interface.user)


def test_redirect_interface() -> None:
    assert isinstance(database_interface.redirect, RedirectInterface)
    assert isinstance(remote_interface.redirect, RedirectInterface)

    # for mypy
    def use_redirect_generic(redirect: RedirectInterface[OpenedResourceT]) -> None:
        pass

    use_redirect_generic(database_interface.redirect)
    use_redirect_generic(remote_interface.redirect)

    def use_redirect_asyncsession(redirect: RedirectInterface[AsyncSession]) -> None:
        pass

    use_redirect_asyncsession(database_interface.redirect)

    def use_redirect_asyncclient(redirect: RedirectInterface[AsyncClient]) -> None:
        pass

    use_redirect_asyncclient(remote_interface.redirect)


def test_log_interface() -> None:
    assert isinstance(database_interface.log, LogInterface)
    assert isinstance(remote_interface.log, LogInterface)

    # for mypy
    def use_log_generic(log: LogInterface[OpenedResourceT]) -> None:
        pass

    use_log_generic(database_interface.log)
    use_log_generic(remote_interface.log)

    def use_log_asyncsession(log: LogInterface[AsyncSession]) -> None:
        pass

    use_log_asyncsession(database_interface.log)

    def use_log_asyncclient(log: LogInterface[AsyncClient]) -> None:
        pass

    use_log_asyncclient(remote_interface.log)


def do_not_run() -> None:
    "for mypy"
    # reveal_type(database_interface.user.remove_by_id)
    # reveal_type(remote_interface.user.remove_by_id)
    # reveal_type(UserInterface.remove_by_id)
    # reveal_type(database_interface.user.update)
    # reveal_type(remote_interface.user.update)
    # reveal_type(UserInterface.update)

    # reveal_type(database_interface.redirect.remove_by_id)
    # reveal_type(remote_interface.redirect.remove_by_id)
    # reveal_type(RedirectInterface.remove_by_id)
    # reveal_type(database_interface.redirect.update)
    # reveal_type(remote_interface.redirect.update)
    # reveal_type(RedirectInterface.update)
