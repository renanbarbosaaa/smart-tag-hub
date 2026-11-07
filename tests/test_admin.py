import re

from httpx import AsyncClient

from tests.conftest import TEST_PASSWORD, TEST_USERNAME


def csrf_from(response_text: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
    assert match is not None
    return match.group(1)


async def login(client: AsyncClient) -> None:
    page = await client.get("/admin/login")
    response = await client.post(
        "/admin/login",
        data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "csrf_token": csrf_from(page.text),
        },
    )
    assert response.status_code == 303


async def test_admin_requires_login(unauthenticated_client: AsyncClient) -> None:
    response = await unauthenticated_client.get("/admin")

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


async def test_login_rejects_invalid_credentials(
    unauthenticated_client: AsyncClient,
) -> None:
    page = await unauthenticated_client.get("/admin/login")

    response = await unauthenticated_client.post(
        "/admin/login",
        data={
            "username": TEST_USERNAME,
            "password": "wrong-password",
            "csrf_token": csrf_from(page.text),
        },
    )

    assert response.status_code == 401
    assert "Usuário ou senha inválidos" in response.text


async def test_login_with_unicode_username_does_not_raise(
    unauthenticated_client: AsyncClient,
) -> None:
    page = await unauthenticated_client.get("/admin/login")

    response = await unauthenticated_client.post(
        "/admin/login",
        data={
            "username": "admínistrador",
            "password": TEST_PASSWORD,
            "csrf_token": csrf_from(page.text),
        },
    )

    assert response.status_code == 401


async def test_login_is_throttled_after_repeated_failures(
    unauthenticated_client: AsyncClient,
) -> None:
    page = await unauthenticated_client.get("/admin/login")
    csrf_token = csrf_from(page.text)
    for _ in range(5):
        response = await unauthenticated_client.post(
            "/admin/login",
            data={
                "username": TEST_USERNAME,
                "password": "wrong-password",
                "csrf_token": csrf_token,
            },
        )
        assert response.status_code == 401
        csrf_token = csrf_from(response.text)

    response = await unauthenticated_client.post(
        "/admin/login",
        data={
            "username": TEST_USERNAME,
            "password": "wrong-password",
            "csrf_token": csrf_token,
        },
    )

    assert response.status_code == 429


async def test_login_and_manage_link_through_panel(
    unauthenticated_client: AsyncClient,
) -> None:
    await login(unauthenticated_client)
    dashboard = await unauthenticated_client.get("/admin")
    assert dashboard.status_code == 200

    created = await unauthenticated_client.post(
        "/admin/links",
        data={
            "target_url": "https://example.com/inicial",
            "slug": "abc123",
            "csrf_token": csrf_from(dashboard.text),
        },
    )
    assert created.status_code == 303

    dashboard = await unauthenticated_client.get("/admin")
    assert "abc123" in dashboard.text
    assert "https://example.com/inicial" in dashboard.text

    edit_page = await unauthenticated_client.get("/admin/links/abc123/edit")
    updated = await unauthenticated_client.post(
        "/admin/links/abc123/edit",
        data={
            "target_url": "https://example.com/atualizado",
            "csrf_token": csrf_from(edit_page.text),
        },
    )
    assert updated.status_code == 303

    dashboard = await unauthenticated_client.get("/admin")
    deactivated = await unauthenticated_client.post(
        "/admin/links/abc123/status",
        data={
            "action": "deactivate",
            "csrf_token": csrf_from(dashboard.text),
        },
    )
    assert deactivated.status_code == 303
    redirect = await unauthenticated_client.get("/r/abc123")
    assert redirect.status_code == 404


async def test_admin_form_rejects_invalid_csrf(
    unauthenticated_client: AsyncClient,
) -> None:
    await login(unauthenticated_client)

    response = await unauthenticated_client.post(
        "/admin/links",
        data={
            "target_url": "https://example.com",
            "csrf_token": "token-não-ascii",
        },
    )

    assert response.status_code == 403


async def test_logout(unauthenticated_client: AsyncClient) -> None:
    await login(unauthenticated_client)
    dashboard = await unauthenticated_client.get("/admin")

    response = await unauthenticated_client.post(
        "/admin/logout", data={"csrf_token": csrf_from(dashboard.text)}
    )
    protected = await unauthenticated_client.get("/api/links")

    assert response.status_code == 303
    assert protected.status_code == 401
