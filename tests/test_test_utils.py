"""
tests the utilities used in other tests
"""
from mw_url_shortener.api.authentication import password_context
from .utils import random_username, random_hashed_password, random_user
from mw_url_shortener.types import Username, HashedPassword
from mw_url_shortener.database import user


def test_random_hashed_password() -> None:
    "does random_hashed_password generate a valid password"
    example_hashed_password: HashedPassword = random_hashed_password()
    
    # NOTE:BUG::TYPES Needs to be HashedPassword
    assert isinstance(example_hashed_password, str), "hashed password must be of type str"
    assert password_context.identify(example_hashed_password) == "bcrypt"


def test_random_username() -> None:
    "does random_username generate a Username that's 1 to 10 characters long"
    example_username: Username = random_username()

    # NOTE:BUG::TYPES Needs to be Username
    assert isinstance(example_username, str), "username must be of type str"
    assert 1 <= len(example_username) <= 10, "username must be between 1 and 10 characters, inclusive"


def test_random_user() -> None:
    "does random_user generate a valid user model"
    example_user: user.Model = random_user()

    # Validate that the model is valid
    generated_model = user.Model(**example_user.dict())
    assert example_user == generated_model
