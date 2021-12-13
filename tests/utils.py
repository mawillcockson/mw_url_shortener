"""
utilities used by the tests

generally, these may be called multiple times in a test, and provide unique
values each time they're called

they could be written as pytest fixtures if they returned the named functions,
but the function signatures would have to be imported from conftest.py, and it
would be easier to import the function directly
"""
from collections import UserString
from random import randint

from mw_url_shortener.settings import defaults
from mw_url_shortener.utils import (
    unsafe_random_printable_string as random_printable_string,
)


def random_username() -> str:
    "creates a random username"
    return random_printable_string(randint(0, defaults.max_username_length))


def random_password() -> str:
    "creates a random pssword"
    return random_printable_string(randint(0, defaults.max_password_length))
