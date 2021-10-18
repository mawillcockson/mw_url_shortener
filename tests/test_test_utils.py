"""
tests the utilities used in other tests
"""
import string

import pytest
from pony.orm import Database

from mw_url_shortener import config
from mw_url_shortener.api.authentication import password_context
from mw_url_shortener.database import get_db, user
from mw_url_shortener.database.interface import setup_db
from mw_url_shortener.settings import (
    CommonSettings,
    DatabaseSettings,
    SettingsClassName,
)
from mw_url_shortener.types import HashedPassword, Username

from .conftest import BadSettings
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
    "does all_keys() generate the same number of items as there are combinations"
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


def test_settings_match(
    correct_settings: CommonSettings, correct_database_settings: DatabaseSettings
) -> None:
    "does DatabaseSettings only add a database_file"
    correct_settings_dict = correct_settings.copy().dict()
    correct_settings_dict.update(
        {"database_file": correct_database_settings.database_file}
    )
    assert correct_settings_dict == correct_database_settings.dict()


def test_same_database(
    database: Database, correct_database_settings: DatabaseSettings
) -> None:
    "is the database_file the same file used for the database"
    # Create a new Database object using the database_file
    database_from_settings = setup_db(
        db=get_db(),
        filename=correct_database_settings.database_file,
        create_tables=False,
    )
    # Show that the fixture database is empty
    with pytest.raises(ValueError):
        config.get_from_db(db=database)
    # Add the settings to the created Database object
    config.save_to_db(db=database_from_settings, new_settings=correct_database_settings)

    # Retrieve the settings from the fixture database object, showing that the
    # database_file points to a database file that, when manipulated,
    # manipulates the same database that the fixture provides
    assert config.get_from_db(db=database) == correct_database_settings


def test_bad_settings(bad_settings: BadSettings) -> None:
    f"""
    does the bad_settings fixture produce an object that derives from
    {CommonSettings}, has a class name that is ok, but is not an ok settings
    object to use
    """
    assert isinstance(bad_settings, CommonSettings)
    assert SettingsClassName.validate(type(bad_settings).__name__)
    with pytest.raises(ValueError):
        SettingsClassName.validate(type(bad_settings))
