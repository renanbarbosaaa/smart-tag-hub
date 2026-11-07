from dataclasses import replace

from api.security import hash_password, verify_admin_credentials
from tests.conftest import TEST_PASSWORD, TEST_SETTINGS


def test_password_hash_and_verification() -> None:
    password_hash = hash_password("a-secure-password")
    settings = replace(TEST_SETTINGS, admin_password_hash=password_hash)

    assert password_hash != "a-secure-password"
    assert verify_admin_credentials(
        TEST_SETTINGS.admin_username, "a-secure-password", settings
    )
    assert not verify_admin_credentials(TEST_SETTINGS.admin_username, "wrong", settings)


def test_invalid_or_missing_hash_fails_closed() -> None:
    missing = replace(TEST_SETTINGS, admin_password_hash="")
    malformed = replace(TEST_SETTINGS, admin_password_hash="not-a-hash")

    assert not verify_admin_credentials(
        TEST_SETTINGS.admin_username, TEST_PASSWORD, missing
    )
    assert not verify_admin_credentials(
        TEST_SETTINGS.admin_username, TEST_PASSWORD, malformed
    )
