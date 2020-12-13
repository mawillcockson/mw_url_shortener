"""
tests the utilities used in other tests
"""
import string

import pytest

from mw_url_shortener.api.authentication import password_context
from mw_url_shortener.database import user
from mw_url_shortener.types import HashedPassword, Username

from .utils import (
    all_combinations,
    random_hashed_password,
    random_user,
    random_username,
)


def test_random_hashed_password() -> None:
    "does random_hashed_password generate a valid password"
    example_hashed_password: HashedPassword = random_hashed_password()

    # NOTE:BUG::TYPES Needs to be HashedPassword
    assert isinstance(
        example_hashed_password, str
    ), "hashed password must be of type str"
    assert password_context.identify(example_hashed_password) == "bcrypt"


def test_random_username() -> None:
    "does random_username generate a Username that's 1 to 10 characters long"
    example_username: Username = random_username()

    # NOTE:BUG::TYPES Needs to be Username
    assert isinstance(example_username, str), "username must be of type str"
    assert (
        1 <= len(example_username) <= 10
    ), "username must be between 1 and 10 characters, inclusive"


def test_random_user() -> None:
    "does random_user generate a valid user model"
    example_user: user.Model = random_user()

    # Validate that the model is valid
    generated_model = user.Model(**example_user.dict())
    assert example_user == generated_model


@pytest.mark.timeout(5)
def test_all_combinations_bad_types() -> None:
    "does all_combinations raise TypeErrors on bad input types"
    with pytest.raises(TypeError) as err:
        all_combinations(characters=object(), length=1)
    assert "characters must be a str of 1 or more characters" in str(err.value)

    with pytest.raises(TypeError) as err:
        all_combinations(characters="abc", length=1.1)
    assert "length must be a positive int greater than 0" in str(err.value)


@pytest.mark.timeout(5)
def test_all_combinations() -> None:
    "does all keys generate the same number of items as there are combinations"
    characters = string.ascii_letters + string.digits
    length: int = 3
    all_three_character_combinations = list(
        all_combinations(characters=characters, length=length)
    )
    number_of_three_character_combinations = len(characters) ** length
    assert number_of_three_character_combinations == 238328
    assert (
        len(all_three_character_combinations) == number_of_three_character_combinations
    )

    def is_three_character_str(value: str) -> bool:
        "is value a str of 3 characters"
        return isinstance(value, str) and len(value) == 3

    assert all(map(is_three_character_str, all_three_character_combinations))
