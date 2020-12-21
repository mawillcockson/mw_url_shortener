"""
These tests are meant to ensure that tests are being properly isolated

They usually come in pairs, and each pair needs to be run in the order that
they are presented in this file
"""
from unittest.mock import _SentinelObject as Sentinel
import os
import pytest
from mw_url_shortener import settings
from typing import Tuple


def test_environment_starts_empty() -> None:
    "does the environment start with only pytest's settings"
    assert list(os.environ) == ["PYTEST_CURRENT_TEST"]


def test_environment_isolation_set(random_env_var_names: Tuple[str, str]) -> None:
    "set environment variables that _check will look for"
    assert os.getenv(random_env_var_names[0], None) is None
    assert os.getenv(random_env_var_names[1], None) is None
    os.environ[random_env_var_names[0]] = "example"
    os.putenv(random_env_var_names[1], "demo")
    assert os.getenv(random_env_var_names[0], None) == "example"
    # NOTE:BUG why is the below statement true?????
    assert os.getenv(random_env_var_names[1], None) is None


def test_environment_isolation_check(random_env_var_names: Tuple[str, str]) -> None:
    """
    checks to make sure the environment variables set in one test don't show up
    in another test
    """
    assert os.getenv(random_env_var_names[0], None) is None
    assert os.getenv(random_env_var_names[1], None) is None
    with pytest.raises(KeyError):
        os.environ[random_env_var_names[0]]
    with pytest.raises(KeyError):
        os.environ[random_env_var_names[1]]


def test_settings_cache_cleared_set(session_sentinel: Sentinel) -> None:
    "sets the settings._settings cache for another test to check"
    # It's important to use a unique object here, to indicate that it won't
    # have come from the internals of mw_url_shortener
    settings._settings = session_sentinel
    assert settings._settings == session_sentinel


def test_settings_cache_cleared_check() -> None:
    """
    checks if the settings cache is cleared between runs
    
    relies on test_settings_cache_cleared_set to be run first
    """
    assert settings._settings is None
