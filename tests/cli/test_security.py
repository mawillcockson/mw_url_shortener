from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import inject
import pytest
from jose import jwt

from mw_url_shortener.cli.entry_point import app
from mw_url_shortener.schemas.user import Username
from mw_url_shortener.server.settings import server_defaults

if TYPE_CHECKING:
    from .conftest import CommandRunner

jwt_options_defaults = {
    "verify_signature": True,
    "verify_aud": True,
    "verify_iat": True,
    "verify_exp": True,
    "verify_nbf": True,
    "verify_iss": True,
    "verify_sub": True,
    "verify_jti": True,
    "verify_at_hash": True,
    "require_aud": False,
    "require_iat": False,
    "require_exp": False,
    "require_nbf": False,
    "require_iss": False,
    "require_sub": False,
    "require_jti": False,
    "require_at_hash": False,
    "leeway": 0,
}


@pytest.mark.parametrize(
    "token_expiration",
    [
        datetime.min.isoformat(),
        datetime.min.isoformat(),
        "1970-01-01T00:00",
        (datetime.now().astimezone() + timedelta(days=365)).isoformat(),
        "2000-01-01T00:00",
    ],
)
async def test_make_token(
    run_test_command: "CommandRunner", token_expiration: str
) -> None:
    jwt_secret_key = ""
    result = await run_test_command(
        app,
        [
            "security",
            "make-token",
            "--username",
            "test",
            "--token-expiration",
            token_expiration,
            "--jwt-secret-key",
            jwt_secret_key,
        ],
        add_default_parameters=False,
    )
    assert result.exit_code == 0, f"result: {result}"
    token_text = result.stdout.strip()
    assert token_text
    jwt_options = jwt_options_defaults.copy()
    jwt_options.update({"verify_exp": False})
    jwt.decode(
        token_text,
        jwt_secret_key,
        algorithms=server_defaults.jwt_hash_algorithm,
        options=jwt_options,
    )

    inject.clear()


@pytest.mark.parametrize(
    "username",
    [
        "",
        "a" * min(abs(Username.min_length - 1), 0),
        "a" * (Username.max_length + 1),
    ],
)
async def test_make_token_bad_username(
    run_test_command: "CommandRunner", username: str
) -> None:
    jwt_secret_key = ""
    result = await run_test_command(
        app,
        [
            "security",
            "make-token",
            "--username",
            username,
            "--token-expiration",
            "2000-01-01T00:00",
            "--jwt-secret-key",
            jwt_secret_key,
        ],
        add_default_parameters=False,
    )
    assert result.exit_code == 1, f"result: {result}"
    assert "bad username" in result.stdout
