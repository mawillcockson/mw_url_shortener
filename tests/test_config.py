"""
ensures mw_url_shortener.config behaves correctly
"""
from mw_url_shortener import config
import pytest


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
def test_get() -> None:
    "config.get()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_export() -> None:
    "config.export()"
    raise NotImplementedError


@pytest.mark.xfail()
def test_write_dotenv() -> None:
    "config.write_dotenv()"
    raise NotImplementedError
