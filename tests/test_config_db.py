"""
ensures the database portion of mw_url_shortener.config behaves correctly
"""
import pytest
from pony.orm import Database

from mw_url_shortener import config, settings
from mw_url_shortener.settings import CommonSettings, DatabaseSettings


@pytest.mark.xfail  # NOTE:NEXT
def test_get_updates_from_db(
    database: Database, correct_database_settings: DatabaseSettings
) -> None:
    """
    will config.get() update the module cache if the only place with settings
    is the database
    """
    assert settings._settings is None
    config.save_to_db(db=database, new_settings=correct_database_settings)

    returned_settings = config.get()
    assert returned_settings == correct_database_settings
    assert settings._settings == correct_database_settings
