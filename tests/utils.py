"""
utilities used by the tests

generally, these are utilities that can't work as pytest fixtures, since pytest fixtures provide the same value all throught a single test function, regardless of scope
"""
from random import randint

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
        )
