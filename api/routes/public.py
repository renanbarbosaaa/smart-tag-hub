from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import LinkServiceDep
from api.templating import templates
from domain.validators import is_valid_slug
from infrastructure.database import get_session

router = APIRouter()


def _public_error(request: Request, status_code: int, message: str) -> Response:
    if "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            request=request,
            name="public_error.html",
            context={"message": message},
            status_code=status_code,
        )
    return JSONResponse(status_code=status_code, content={"detail": message})


@router.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Smart Tag Hub está operacional."}


@router.get("/_health")
async def health_check(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível.",
        ) from exc
    return {"status": "ok"}


@router.get("/r/{slug}", name="redirect_short")
@router.get("/{slug}", include_in_schema=False)
async def redirect_to_target(
    slug: str, request: Request, service: LinkServiceDep
) -> Response:
    if not is_valid_slug(slug):
        return _public_error(request, 400, "Slug com formato inválido.")

    target_url = await service.resolve(slug)
    if target_url is None:
        return _public_error(request, 404, "Link não encontrado ou desativado.")

    return RedirectResponse(
        url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
