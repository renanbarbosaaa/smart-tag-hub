from urllib.parse import urlparse

SLUG_LENGTH = 6
MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}


def is_valid_slug(slug: str) -> bool:
    return len(slug) == SLUG_LENGTH and slug.isascii() and slug.isalnum()


def is_valid_url(url: str) -> bool:
    if len(url) > MAX_URL_LENGTH:
        return False

    try:
        parsed_url = urlparse(url)
    except ValueError:
        return False

    return (
        parsed_url.scheme in ALLOWED_SCHEMES
        and bool(parsed_url.netloc)
        and bool(parsed_url.path)
    )