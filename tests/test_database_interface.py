from pony.orm import Database

from mw_url_shortener.database.config import get_config, save_config
from mw_url_shortener.settings import CommonSettings


def test_save_config(database: Database, correct_settings: CommonSettings) -> None:
    "Tests if a config can be saved and read back correctly"
    save_config(db=database, settings=correct_settings)
    returned_settings = get_config(db=database)
    assert correct_settings == returned_settings
