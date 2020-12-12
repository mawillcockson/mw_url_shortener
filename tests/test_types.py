"""
test that the types behave in specific ways
"""
import pytest

from mw_url_shortener.types import HashedPassword, Key, PlainPassword, Uri, Username

from .utils import random_hashed_password, random_username


@pytest.mark.xfail(raises=NotImplementedError)
def test_username() -> None:
    "can usernames be shorter than 1 character"
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_hashedpassword() -> None:
    "are hashed passwords verified to be usable by the password context"
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_uri() -> None:
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_key() -> None:
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_plainpassword() -> None:
    raise NotImplementedError
