print(f"imported mw_url_shortener.database.config as {__name__}")
from pony.orm import Database, db_session

from .. import settings
from ..settings import CommonSettings, SettingsClasses, SettingsClassName


def get_config(db: Database) -> CommonSettings:
    "retrieves and deserializes CommonSettings from the database"
    with db_session:
        current_config = db.ConfigEntity.get(version="current")

        if not current_config:
            raise ValueError("No current config")

        current_config_json = current_config.json
        class_name = SettingsClassName.validate(current_config.class_name)
        settings_class = getattr(settings, class_name)

    return settings_class.parse_raw(current_config_json)


def save_config(db: Database, new_settings: CommonSettings) -> CommonSettings:
    "encodes the settings and writes them to the database"
    class_name = SettingsClassName.validate(new_settings.__class__.__name__)
    with db_session:
        config_entity = db.ConfigEntity(
            version="current", class_name=class_name, json=new_settings.json()
        )
        return new_settings.__class__.parse_raw(config_entity.json)
