from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from api.config import get_settings
from api.routes import admin, links, public
from api.security import AdminPageLoginRequired
from domain.exceptions import (
    DomainError,
    InvalidSlugError,
    InvalidUrlError,
    SlugAlreadyExistsError,
    SlugGenerationError,
)
from infrastructure.database import engine

_ERROR_STATUS: dict[type[DomainError], int] = {
    InvalidUrlError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidSlugError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    SlugAlreadyExistsError: status.HTTP_409_CONFLICT,
    SlugGenerationError: status.HTTP_503_SERVICE_UNAVAILABLE,
}

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings.validate()
    yield
    await engine.dispose()


app = FastAPI(
    title="Smart Tag Hub",
    version="1.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="smart_tag_session",
    max_age=settings.session_max_age,
    same_site="lax",
    https_only=settings.session_secure_cookie,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
app.mount(
    "/_static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; base-uri 'self'; frame-ancestors 'none'; "
        "form-action 'self'"
    )
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    code = _ERROR_STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=code, content={"detail": str(exc)})


@app.exception_handler(AdminPageLoginRequired)
async def admin_login_required_handler(
    _: Request, __: AdminPageLoginRequired
) -> RedirectResponse:
    return RedirectResponse("/admin/login", status_code=status.HTTP_303_SEE_OTHER)


app.include_router(links.router)
app.include_router(links.legacy_router)
app.include_router(admin.router)
app.include_router(public.router)
