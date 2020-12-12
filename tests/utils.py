from mw_url_shortener.database import user
from random import randint
from mw_url_shortener.utils import unsafe_random_hashed_password as random_hashed_password, random_username as rand_username
from mw_url_shortener.types import Username, HashedPassword


def random_username() -> Username:
    "creates an example username"
    return rand_username(randint(1,10))


def random_user() -> user.Model:
    "creates a fictitious user that doesn't exist in the database"
    return user.Model(
            username=random_username(),
            hashed_password=random_hashed_password(),
        )
