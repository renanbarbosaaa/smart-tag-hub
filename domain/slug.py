import secrets
import string

SLUG_LENGTH = 6
SLUG_ALPHABET = string.ascii_letters + string.digits


def generate_slug() -> str:
    return "".join(secrets.choice(SLUG_ALPHABET) for _ in range(SLUG_LENGTH))