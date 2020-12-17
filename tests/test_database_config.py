from pathlib import Path

import pydantic
import pytest
from pony.orm import Database, db_session

from mw_url_shortener.database.config import get_config, save_config
from mw_url_shortener.database.errors import BadConfigInDBError
from mw_url_shortener.settings import CommonSettings

from .utils import random_json


def test_save_and_load_config(
    database: Database, correct_settings: CommonSettings
) -> None:
    "can a config be saved and read back correctly"
    saved_settings = save_config(db=database, new_settings=correct_settings)
    returned_settings = get_config(db=database)
    assert correct_settings == saved_settings == returned_settings


def test_load_bad_config(database: Database) -> None:
    "is an error thrown if a bad config is read from the database"
    example_bad_json: str = random_json()
    # Prove the example_bad_json is not a valid configuration structure
    with pytest.raises(pydantic.ValidationError) as err:
        CommonSettings.parse_raw(example_bad_json)

    with db_session:
        database.ConfigEntity(
            version="current", json=example_bad_json, class_name=CommonSettings.__name__
        )
        database.commit()

    with pytest.raises(BadConfigInDBError) as err:
        get_config(db=database)
    assert "bad configuration in database" in str(err.value)


def test_save_bad_config(database: Database, correct_settings: CommonSettings) -> None:
    "is an error thrown when a bad config is saved"

    class DummyClass(pydantic.BaseSettings):
        f"a dummy class meant to mimic {CommonSettings.__name__}"
        env_file: Path = correct_settings.env_file

    bad_settings = DummyClass()
    bad_settings.__class__.__name__ = CommonSettings.__name__

    with pytest.raises(ValueError) as err:
        save_config(db=database, new_settings=bad_settings)
    assert "new_settings must be an instance of a settings class" in str(err.value)
