import pytest
from pony.orm import Database, db_session
from mw_url_shortener.database.config import get_config, save_config
from mw_url_shortener.settings import CommonSettings
from mw_url_shortener.database.errors import BadConfigError


def test_save_config(database: Database, correct_settings: CommonSettings) -> None:
    "can a config be saved and read back correctly"
    save_config(db=database, settings=correct_settings)
    returned_settings = get_config(db=database)
    assert correct_settings == returned_settings


@pytest.mark.xfail
def test_load_bad_config(database: Database, random_json: str) -> None:
    "is an error thrown if a bad config is read from the database"
    with db_session:
        database.ConfigEntity(version="current", json=random_json())
        database.commit()

    with pytest.raises(BadConfigError) as err:
        get_config(db=database)
    assert "bad configuration in database" in str(err.value)


@pytest.mark.xfail
def test_save_bad_config(database: Database, random_json: str) -> None:
    "is an error thrown when a bad config is saved"
    with pytest.raises(BadConfigError) as err:
        save_config(db=database, settings=random_json)
    assert "bad configuration data" in str(err.value)
