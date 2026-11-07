from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response

from api.config import Settings, get_settings
from api.deps import LinkServiceDep
from api.security import (
    AdminPageDep,
    get_csrf_token,
    login_attempt_limiter,
    validate_csrf,
    verify_admin_credentials,
)
from api.templating import templates
from domain.exceptions import DomainError, SlugAlreadyExistsError
from domain.models import Link
from domain.services import LinkService

router = APIRouter(prefix="/admin", include_in_schema=False)


def _short_url(request: Request, slug: str) -> str:
    return f"{str(request.base_url).rstrip('/')}/r/{slug}"


def _login_response(
    request: Request,
    *,
    error: str | None = None,
    status_code: int = 200,
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": error, "csrf_token": get_csrf_token(request)},
        status_code=status_code,
    )


async def _dashboard_response(
    request: Request,
    service: LinkService,
    *,
    query: str | None = None,
    error: str | None = None,
    notice: str | None = None,
    target_url: str = "",
    slug: str = "",
    status_code: int = 200,
) -> Response:
    links = await service.list_links(query)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "links": links,
            "query": query or "",
            "error": error,
            "notice": notice,
            "target_url": target_url,
            "slug": slug,
            "csrf_token": get_csrf_token(request),
            "short_url": lambda value: _short_url(request, value),
        },
        status_code=status_code,
    )


def _edit_response(
    request: Request,
    link: Link,
    *,
    error: str | None = None,
    status_code: int = 200,
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="edit_link.html",
        context={
            "link": link,
            "error": error,
            "csrf_token": get_csrf_token(request),
            "short_url": _short_url(request, link.slug),
        },
        status_code=status_code,
    )


@router.get("/login")
async def login_page(request: Request) -> Response:
    if request.session.get("is_admin") is True:
        return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
    return _login_response(request)


@router.post("/login")
async def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    csrf_token: Annotated[str, Form()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    validate_csrf(request, csrf_token)
    client_key = request.client.host if request.client else "unknown"
    if not login_attempt_limiter.is_allowed(client_key):
        return _login_response(
            request,
            error="Muitas tentativas. Aguarde alguns minutos e tente novamente.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if not verify_admin_credentials(username, password, settings):
        login_attempt_limiter.record_failure(client_key)
        return _login_response(
            request,
            error="Usuário ou senha inválidos.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    login_attempt_limiter.reset(client_key)
    request.session.clear()
    request.session["is_admin"] = True
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout(
    request: Request,
    _: AdminPageDep,
    csrf_token: Annotated[str, Form()],
) -> RedirectResponse:
    validate_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("")
async def dashboard(
    request: Request,
    service: LinkServiceDep,
    _: AdminPageDep,
    q: str | None = None,
    created: str | None = None,
    updated: str | None = None,
) -> Response:
    notice = None
    if created:
        notice = f"Link {created} criado com sucesso."
    elif updated:
        notice = f"Link {updated} atualizado com sucesso."
    return await _dashboard_response(request, service, query=q, notice=notice)


@router.post("/links")
async def create_link_page(
    request: Request,
    service: LinkServiceDep,
    _: AdminPageDep,
    target_url: Annotated[str, Form()],
    csrf_token: Annotated[str, Form()],
    slug: Annotated[str | None, Form()] = None,
) -> Response:
    validate_csrf(request, csrf_token)
    try:
        link = await service.create_link(target_url.strip(), slug or None)
    except DomainError as exc:
        error_status = (
            status.HTTP_409_CONFLICT
            if isinstance(exc, SlugAlreadyExistsError)
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        return await _dashboard_response(
            request,
            service,
            error=str(exc),
            target_url=target_url,
            slug=slug or "",
            status_code=error_status,
        )
    return RedirectResponse(
        f"/admin?created={link.slug}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/links/{slug}/edit")
async def edit_link_page(
    request: Request, slug: str, service: LinkServiceDep, _: AdminPageDep
) -> Response:
    link = await service.get_link(slug)
    if link is None:
        raise HTTPException(status_code=404, detail="Link não encontrado.")
    return _edit_response(request, link)


@router.post("/links/{slug}/edit")
async def update_link_page(
    request: Request,
    slug: str,
    service: LinkServiceDep,
    _: AdminPageDep,
    target_url: Annotated[str, Form()],
    csrf_token: Annotated[str, Form()],
) -> Response:
    validate_csrf(request, csrf_token)
    try:
        link = await service.update_link(slug, target_url=target_url.strip())
    except DomainError as exc:
        current = await service.get_link(slug)
        if current is None:
            raise HTTPException(status_code=404, detail="Link não encontrado.") from exc
        return _edit_response(
            request,
            current,
            error=str(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    if link is None:
        raise HTTPException(status_code=404, detail="Link não encontrado.")
    return RedirectResponse(
        f"/admin?updated={link.slug}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/links/{slug}/status")
async def update_link_status_page(
    request: Request,
    slug: str,
    service: LinkServiceDep,
    _: AdminPageDep,
    action: Annotated[str, Form()],
    csrf_token: Annotated[str, Form()],
) -> RedirectResponse:
    validate_csrf(request, csrf_token)
    if action not in {"activate", "deactivate"}:
        raise HTTPException(status_code=400, detail="Ação inválida.")
    link = await service.update_link(slug, is_active=action == "activate")
    if link is None:
        raise HTTPException(status_code=404, detail="Link não encontrado.")
    return RedirectResponse(
        f"/admin?updated={link.slug}", status_code=status.HTTP_303_SEE_OTHER
    )
