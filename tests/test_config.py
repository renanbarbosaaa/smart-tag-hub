from dataclasses import replace

import pytest

from api.config import Settings
from tests.conftest import TEST_SETTINGS


def production_settings() -> Settings:
    return replace(
        TEST_SETTINGS,
        environment="production",
        database_url="postgresql+asyncpg://user:password@db.example.com/smart_tag_hub",
        database_url_explicit=True,
        allowed_hosts=("api.example.com",),
        session_secure_cookie=True,
    )


def test_valid_production_settings() -> None:
    production_settings().validate()


def test_absolute_sqlite_path_is_allowed_when_explicit() -> None:
    settings = replace(
        production_settings(),
        database_url="sqlite+aiosqlite:////app/data/smart_tag_hub.db",
    )

    settings.validate()


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"secret_key": "short"}, "SECRET_KEY"),
        ({"secret_key": "substitua-por-uma-chave-aleatoria-longa"}, "SECRET_KEY"),
        ({"admin_password_hash": ""}, "ADMIN_PASSWORD_HASH"),
        ({"admin_password_hash": "cole-aqui-o-hash"}, "ADMIN_PASSWORD_HASH"),
        ({"allowed_hosts": ("*",)}, "ALLOWED_HOSTS"),
        ({"session_secure_cookie": False}, "SESSION_SECURE_COOKIE"),
        ({"database_url_explicit": False}, "DATABASE_URL"),
        (
            {"database_url": "sqlite+aiosqlite:///./smart_tag_hub.db"},
            "volume persistente",
        ),
        ({"database_url": "sqlite+aiosqlite://"}, "volume persistente"),
    ],
)
def test_invalid_production_settings(changes: dict, message: str) -> None:
    settings = replace(production_settings(), **changes)

    with pytest.raises(RuntimeError, match=message):
        settings.validate()
