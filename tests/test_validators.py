import pytest

from domain.validators import is_valid_slug, is_valid_url


@pytest.mark.parametrize("slug", ["aX7b9Y", "123456", "abcdef"])
def test_valid_slugs(slug: str) -> None:
    assert is_valid_slug(slug)


@pytest.mark.parametrize("slug", ["abcde", "aX7b9Y1", ""])
def test_slug_with_wrong_size(slug: str) -> None:
    assert not is_valid_slug(slug)


@pytest.mark.parametrize(
    "slug", ["aX-b9Y", "aX7b 9", "drop x", "aX7b9@", "ção123", "١٢٣٤٥٦"]
)
def test_slug_with_invalid_characters(slug: str) -> None:
    assert not is_valid_slug(slug)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.pathto.com.br/test1",
        "https://www.linkedin.com/in/renan",
        "https://api.dominio.com/v1/users?id=1",
        "http://meusite.com.br",
        "https://meusite.com.br?origem=nfc",
    ],
)
def test_valid_urls(url: str) -> None:
    assert is_valid_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "",
        "www.google.com",
        "javascript:alert(1)",
        "ftp://meuserver.com/arquivo.zip",
        "http://[::1/path",
        "http://example.com:invalid/path",
        "https://example.com/espaco no destino",
    ],
)
def test_invalid_urls(url: str) -> None:
    assert not is_valid_url(url)


def test_url_over_max_length() -> None:
    base = "https://www.linkedin.com/"
    assert is_valid_url(base + "a" * (2048 - len(base)))
    assert not is_valid_url(base + "a" * (2049 - len(base)))
