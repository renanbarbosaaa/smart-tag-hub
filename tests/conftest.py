from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from api.config import Settings, get_settings
from api.main import app
from api.security import (
    hash_password,
    login_attempt_limiter,
    require_admin_api,
    require_admin_page,
)
from infrastructure import models  # noqa: F401
from infrastructure.database import Base, get_session

TEST_USERNAME = "admin"
TEST_PASSWORD = "test-password"
TEST_SETTINGS = Settings(
    environment="testing",
    database_url="sqlite+aiosqlite://",
    secret_key="test-secret-key-with-at-least-32-characters",
    admin_username=TEST_USERNAME,
    admin_password_hash=hash_password(TEST_PASSWORD),
    allowed_hosts=("testserver",),
    session_secure_cookie=False,
)


@pytest.fixture(autouse=True)
def reset_login_limiter() -> None:
    login_attempt_limiter.reset()


@pytest_asyncio.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS
    app.dependency_overrides[require_admin_api] = lambda: None
    app.dependency_overrides[require_admin_page] = lambda: None
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthenticated_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
