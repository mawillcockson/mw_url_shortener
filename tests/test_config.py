"""
ensures mw_url_shortener.config behaves correctly
"""
import os
from pathlib import Path
from typing import Dict, Union

import pytest
from pydantic import ValidationError

from mw_url_shortener import config
from mw_url_shortener.config import Namespace
from mw_url_shortener.settings import CommonSettings, DatabaseSettings


def test_get_no_args_error() -> None:
    "does get() throw an error if no database file is given"
    with pytest.raises(ValidationError) as err:
        config.get(settings_class=DatabaseSettings)
    assert "database_file" in str(err.value)


@pytest.mark.parametrize("args", [object(), type, {"a": 1}])
def test_get_bad_type(args: Union[object, type, Dict[str, int]]) -> None:
    "does get raise a TypeError if args isn't a Namespace"
    with pytest.raises(TypeError) as err:
        config.get(args=args)
    assert "args must be an argparse.Namespace or None" in str(err.value)


def test_get_database_in_args(tmp_path: Path) -> None:
    "if the database_file is indicated in the args, is it then set in the environment"
    database_file = tmp_path / "temp.sqlitedb"
    resolved_database_file = database_file.resolve()
    resolved_database_file.touch()
    args = Namespace(database_file=database_file)
    settings = config.get(args=args, settings_class=DatabaseSettings)
    assert isinstance(settings, CommonSettings)
    assert settings.database_file == resolved_database_file
    assert os.getenv("URL_SHORTENER_DATABASE_FILE") == str(resolved_database_file)


@pytest.mark.xfail()
def test_from_db() -> None:
    "config.from_db()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_to_db() -> None:
    "config.to_db()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_save() -> None:
    "config.save()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_export() -> None:
    "config.export()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_write_dotenv() -> None:
    "config.write_dotenv()"
    raise NotImplementedError
