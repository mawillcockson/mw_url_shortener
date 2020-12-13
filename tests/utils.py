"""
utilities used by the tests

generally, these are utilities that can't work as pytest fixtures, since pytest fixtures provide the same value all throught a single test function, regardless of scope
"""
import itertools
from random import randint
from typing import Iterable

import faker  # faker fixture required for tests

from mw_url_shortener.database import redirect, user
from mw_url_shortener.types import HashedPassword, Key, Uri, Username
from mw_url_shortener.utils import random_username as rand_username
from mw_url_shortener.utils import (
    unsafe_random_hashed_password as random_hashed_password,
)
from mw_url_shortener.utils import unsafe_random_string as random_string


def random_username() -> Username:
    "creates an example username"
    return rand_username(randint(1, 10))


def random_user() -> user.Model:
    "creates a fictitious user that doesn't exist in the database"
    return user.Model(
        username=random_username(),
        hashed_password=random_hashed_password(),
    )


fake = faker.Faker()
fake.add_provider(faker.providers.misc)
fake.add_provider(faker.providers.internet)


def random_json() -> str:
    "uses faker fixture to generate random json"
    return str(fake.json())


def random_uri() -> Uri:
    "uses faker to generate random URIs"
    return Uri(fake.uri())


def random_key() -> Key:
    """
    uses faker to generate unique random keys

    from:
    https://faker.readthedocs.io/en/stable/providers/faker.providers.misc.html#faker.providers.misc.Provider.password
    """
    # NOTE:BUG Doesn't go below 3 characters in length
    # Need to make a new_redirect_key function
    return Key(
        fake.unique.password(
            length=randint(3, 10),
            special_chars=False,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
    )


def random_redirect() -> redirect.Model:
    "uses faker to generate a random redirect model"
    return redirect.Model(key=random_key(), uri=random_uri())


def all_combinations(characters: str, length: int) -> Iterable[str]:
    """
    gives an iterator that produces all the combinations of characters from a
    set for a particular length
    """
    if not (isinstance(characters, str) and len(characters) > 0):
        raise TypeError("characters must be a str of 1 or more characters")
    if not (isinstance(length, int) and length > 0):
        raise TypeError("length must be a positive int greater than 0")

    def combo_gen() -> Iterable[str]:
        "inner generator"
        for three_str_tuple in itertools.product(set(characters), repeat=length):
            yield "".join(three_str_tuple)

    return combo_gen()
