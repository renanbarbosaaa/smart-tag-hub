from httpx import AsyncClient

from domain.validators import is_valid_slug

TARGET = "https://www.linkedin.com/in/renanbarbosaaa"


async def test_create_link_generates_valid_slug(client: AsyncClient) -> None:
    response = await client.post("/links", json={"target_url": TARGET})

    assert response.status_code == 201
    body = response.json()
    assert is_valid_slug(body["slug"])
    assert body["target_url"] == TARGET
    assert "created_at" in body


async def test_create_link_with_custom_slug(client: AsyncClient) -> None:
    response = await client.post("/links", json={"target_url": TARGET, "slug": "abc123"})

    assert response.status_code == 201
    assert response.json()["slug"] == "abc123"


async def test_duplicate_slug_returns_409(client: AsyncClient) -> None:
    payload = {"target_url": TARGET, "slug": "abc123"}
    await client.post("/links", json=payload)

    response = await client.post("/links", json=payload)

    assert response.status_code == 409


async def test_invalid_url_returns_422(client: AsyncClient) -> None:
    response = await client.post("/links", json={"target_url": "ftp://example.com/x"})

    assert response.status_code == 422


async def test_invalid_custom_slug_returns_422(client: AsyncClient) -> None:
    response = await client.post("/links", json={"target_url": TARGET, "slug": "abc"})

    assert response.status_code == 422


async def test_missing_target_url_returns_422(client: AsyncClient) -> None:
    response = await client.post("/links", json={})

    assert response.status_code == 422


async def test_created_link_redirects_with_307(client: AsyncClient) -> None:
    created = await client.post("/links", json={"target_url": TARGET})
    slug = created.json()["slug"]

    response = await client.get(f"/{slug}")

    assert response.status_code == 307
    assert response.headers["location"] == TARGET


async def test_unknown_slug_returns_404(client: AsyncClient) -> None:
    response = await client.get("/zzzzzz")

    assert response.status_code == 404
    assert response.json()["detail"] == "Link não encontrado."


async def test_malformed_slug_returns_400(client: AsyncClient) -> None:
    response = await client.get("/not-a-slug")

    assert response.status_code == 400
    assert response.json()["detail"] == "Slug com formato inválido."


async def test_root_returns_welcome_message(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()