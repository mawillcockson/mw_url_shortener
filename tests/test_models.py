"""
verify behaviour of models
"""
from typing import Union

import pytest

from mw_url_shortener.database.models import RedirectModel, UserModel


@pytest.mark.xfail(raises=NotImplementedError, reason="no checks implemented yet")
@pytest.mark.parametrize("username", [bytes(range(10)), object(), int(0), int(1)])
def test_non_string_username(username: Union[bytes, object, int]) -> None:
    "can non-string values be given for usernames"
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_bad_hashed_password() -> None:
    "does the user model check that a password is verifiable"
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_redirect_uri_validity() -> None:
    "does the redirect model check the format of the uri"
    raise NotImplementedError


@pytest.mark.xfail(raises=NotImplementedError)
def test_redirect_key_format() -> None:
    """
    does the redirect model verify that the key format matches the current
    settings
    """
    raise NotImplementedError
