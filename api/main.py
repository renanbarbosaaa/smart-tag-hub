from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from api.deps import LinkServiceDep
from api.schemas import LinkCreate, LinkRead
from domain.exceptions import (
    DomainError,
    InvalidSlugError,
    InvalidUrlError,
    SlugAlreadyExistsError,
    SlugGenerationError,
)
from domain.models import Link
from domain.validators import is_valid_slug
from infrastructure.database import create_tables, engine

_ERROR_STATUS: dict[type[DomainError], int] = {
    InvalidUrlError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidSlugError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    SlugAlreadyExistsError: status.HTTP_409_CONFLICT,
    SlugGenerationError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await create_tables()
    yield
    await engine.dispose()


app = FastAPI(title="Smart Tag Hub - Encurtador NFC", version="1.0", lifespan=lifespan)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    code = _ERROR_STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=code, content={"detail": str(exc)})


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Bem-vindo ao backend do encurtador pathto.com.br"}


@app.post("/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
async def create_link(payload: LinkCreate, service: LinkServiceDep) -> Link:
    return await service.create_link(payload.target_url, payload.slug)


@app.get("/{slug}")
async def redirect_to_target(slug: str, service: LinkServiceDep) -> RedirectResponse:
    if not is_valid_slug(slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug com formato inválido.",
        )

    target_url = await service.resolve(slug)
    if target_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link não encontrado.",
        )

    return RedirectResponse(url=target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)