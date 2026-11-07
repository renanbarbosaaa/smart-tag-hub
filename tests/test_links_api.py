import pytest
from httpx import AsyncClient

from domain.validators import is_valid_slug

TARGET = "https://www.linkedin.com/in/renanbarbosaaa"


async def create(client: AsyncClient, slug: str = "abc123", target: str = TARGET):
    return await client.post("/api/links", json={"target_url": target, "slug": slug})


async def test_create_link_generates_valid_slug(client: AsyncClient) -> None:
    response = await client.post("/api/links", json={"target_url": TARGET})

    assert response.status_code == 201
    body = response.json()
    assert is_valid_slug(body["slug"])
    assert body["target_url"] == TARGET
    assert body["is_active"] is True
    assert "created_at" in body


async def test_create_link_with_custom_slug(client: AsyncClient) -> None:
    response = await create(client)

    assert response.status_code == 201
    assert response.json()["slug"] == "abc123"


async def test_legacy_create_route_remains_compatible(client: AsyncClient) -> None:
    response = await client.post(
        "/links", json={"target_url": TARGET, "slug": "abc123"}
    )

    assert response.status_code == 201
    assert response.json()["slug"] == "abc123"


async def test_duplicate_slug_returns_409(client: AsyncClient) -> None:
    await create(client)

    response = await create(client)

    assert response.status_code == 409


async def test_invalid_url_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/links", json={"target_url": "ftp://example.com/x"}
    )

    assert response.status_code == 422


async def test_invalid_custom_slug_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/links", json={"target_url": TARGET, "slug": "abc"}
    )

    assert response.status_code == 422


async def test_missing_target_url_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/links", json={})

    assert response.status_code == 422


async def test_created_link_redirects_with_307(client: AsyncClient) -> None:
    await create(client)

    response = await client.get("/r/abc123")

    assert response.status_code == 307
    assert response.headers["location"] == TARGET


async def test_legacy_route_remains_compatible(client: AsyncClient) -> None:
    await create(client)

    response = await client.get("/abc123")

    assert response.status_code == 307
    assert response.headers["location"] == TARGET


@pytest.mark.parametrize("slug", ["health", "static"])
async def test_legacy_slugs_do_not_collide_with_new_routes(
    client: AsyncClient, slug: str
) -> None:
    await create(client, slug)

    response = await client.get(f"/{slug}")

    assert response.status_code == 307
    assert response.headers["location"] == TARGET


async def test_unknown_slug_returns_404(client: AsyncClient) -> None:
    response = await client.get("/r/zzzzzz")

    assert response.status_code == 404
    assert response.json()["detail"] == "Link não encontrado ou desativado."


async def test_browser_receives_friendly_error_page(client: AsyncClient) -> None:
    response = await client.get("/r/zzzzzz", headers={"accept": "text/html"})

    assert response.status_code == 404
    assert "Link indisponível" in response.text


async def test_malformed_slug_returns_400(client: AsyncClient) -> None:
    response = await client.get("/r/not-a-slug")

    assert response.status_code == 400
    assert response.json()["detail"] == "Slug com formato inválido."


async def test_root_returns_welcome_message(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()


async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/_health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_list_and_filter_links(client: AsyncClient) -> None:
    await create(client)
    await create(client, "xyz789", "https://example.com/destino")

    all_links = await client.get("/api/links")
    filtered = await client.get("/api/links", params={"q": "example.com"})

    assert all_links.status_code == 200
    assert len(all_links.json()) == 2
    assert [item["slug"] for item in filtered.json()] == ["xyz789"]


async def test_get_link(client: AsyncClient) -> None:
    await create(client)

    response = await client.get("/api/links/abc123")

    assert response.status_code == 200
    assert response.json()["target_url"] == TARGET


async def test_update_target_changes_redirect(client: AsyncClient) -> None:
    await create(client)
    new_target = "https://example.com/novo-destino"

    response = await client.patch("/api/links/abc123", json={"target_url": new_target})
    redirect = await client.get("/r/abc123")

    assert response.status_code == 200
    assert response.json()["target_url"] == new_target
    assert redirect.headers["location"] == new_target


async def test_deactivate_and_reactivate_link(client: AsyncClient) -> None:
    await create(client)

    deactivated = await client.patch("/api/links/abc123", json={"is_active": False})
    inactive_redirect = await client.get("/r/abc123")
    reactivated = await client.patch("/api/links/abc123", json={"is_active": True})
    active_redirect = await client.get("/r/abc123")

    assert deactivated.json()["is_active"] is False
    assert inactive_redirect.status_code == 404
    assert reactivated.json()["is_active"] is True
    assert active_redirect.status_code == 307


async def test_update_unknown_link_returns_404(client: AsyncClient) -> None:
    response = await client.patch("/api/links/abc123", json={"target_url": TARGET})

    assert response.status_code == 404


async def test_empty_update_returns_422(client: AsyncClient) -> None:
    await create(client)

    response = await client.patch("/api/links/abc123", json={})

    assert response.status_code == 422


async def test_admin_routes_require_authentication(
    unauthenticated_client: AsyncClient,
) -> None:
    responses = [
        await unauthenticated_client.get("/api/links"),
        await unauthenticated_client.post("/api/links", json={"target_url": TARGET}),
        await unauthenticated_client.get("/api/links/abc123"),
        await unauthenticated_client.patch(
            "/api/links/abc123", json={"is_active": False}
        ),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401, 401]
