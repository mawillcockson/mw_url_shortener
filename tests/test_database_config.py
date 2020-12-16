import pydantic
import pytest
from pony.orm import Database, db_session

from mw_url_shortener.database.config import get_config, save_config
from mw_url_shortener.database.errors import BadConfigError
from mw_url_shortener.settings import CommonSettings

from .utils import random_json


def test_save_and_load_config(
    database: Database, correct_settings: CommonSettings
) -> None:
    "can a config be saved and read back correctly"
    saved_settings = save_config(db=database, settings=correct_settings)
    returned_settings = get_config(db=database)
    assert correct_settings == saved_settings == returned_settings


@pytest.mark.xfail
def test_load_bad_config(database: Database) -> None:
    "is an error thrown if a bad config is read from the database"
    example_bad_json: str = random_json()
    # Prove the example_bad_json is not a valid configuration structure
    try:
        CommonSettings.parse_raw(example_bad_json)
    except pydantic.ValidationError as validation_error:
        pass
    else:
        assert not validation_error

    with db_session:
        database.ConfigEntity(version="current", json=example_bad_json)
        database.commit()

    with pytest.raises(BadConfigError) as err:
        get_config(db=database)
    assert "bad configuration in database" in str(err.value)


@pytest.mark.xfail
def test_save_bad_config(database: Database) -> None:
    "is an error thrown when a bad config is saved"
    example_bad_json: str = random_json()
    # Prove the example_bad_json is not a valid configuration structure
    try:
        CommonSettings.parse_raw(example_bad_json)
    except pydantic.ValidationError as validation_error:
        pass
    else:
        assert not validation_error

    with pytest.raises(BadConfigError) as err:
        save_config(db=database, settings=example_bad_json)
    assert "bad configuration data" in str(err.value)
