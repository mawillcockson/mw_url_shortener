print(f"imported mw_url_shortener.database.config as {__name__}")
from pony.orm import Database, db_session
from ..settings import CommonSettings


def get_config(db: Database) -> CommonSettings:
    "retrieves and deserializes CommonSettings from the database"
    with db_session:
        current_config = db.ConfigEntity.get(version="current")
        
        if not current_config:
            raise ValueError("No current config")

        current_config_json = current_config.json

    return CommonSettings.parse_raw(current_config_json)


def save_config(db:Database, settings: CommonSettings) -> None:
    "encodes the settings and writes them to the database"
    with db_session:
        db.ConfigEntity(version="current", json=settings.json())
