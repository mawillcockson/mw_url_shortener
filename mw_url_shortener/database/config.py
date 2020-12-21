print(f"imported mw_url_shortener.database.config as {__name__}")
from pony.orm import Database, db_session
from pydantic import ValidationError

from .. import settings
from ..settings import CommonSettings, SettingsClasses, SettingsClassName
from .errors import BadConfigInDBError


def get_config(db: Database) -> CommonSettings:
    "retrieves and deserializes CommonSettings from the database"
    with db_session:
        current_config = db.ConfigEntity.get(version="current")

        if not current_config:
            raise ValueError("no current config in database")

        current_config_json = current_config.json
        class_name = SettingsClassName.validate(current_config.class_name)
        settings_class = getattr(settings, class_name)

    try:
        return settings_class.parse_raw(current_config_json)
    except ValidationError as err:
        raise BadConfigInDBError("bad configuration in database") from err


def save_config(db: Database, new_settings: CommonSettings) -> CommonSettings:
    "encodes the settings and writes them to the database"
    bad_class_msg = "new_settings must be an instance of a settings class"
    try:
        class_name = SettingsClassName.validate(new_settings.__class__.__name__)
    except ValidationError as err:
        raise ValueError(bad_class_msg) from err

    settings_class = getattr(settings, class_name)
    if settings_class != type(new_settings):
        raise ValueError(bad_class_msg)

    with db_session:
        config_entity = db.ConfigEntity(
            version="current", class_name=class_name, json=new_settings.json()
        )
        return settings_class.parse_raw(config_entity.json)
