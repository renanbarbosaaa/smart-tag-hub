from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from api.deps import LinkServiceDep
from api.schemas import LinkCreate, LinkRead, LinkUpdate
from api.security import AdminApiDep
from domain.models import Link

router = APIRouter(prefix="/api/links", tags=["links"])
legacy_router = APIRouter(include_in_schema=False)


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Link não encontrado.",
    )


@router.get("", response_model=list[LinkRead])
async def list_links(
    service: LinkServiceDep,
    _: AdminApiDep,
    query: Annotated[str | None, Query(alias="q", max_length=200)] = None,
) -> list[Link]:
    return await service.list_links(query)


@router.post("", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate, service: LinkServiceDep, _: AdminApiDep
) -> Link:
    return await service.create_link(payload.target_url, payload.slug)


@legacy_router.post(
    "/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED
)
async def create_link_legacy(
    payload: LinkCreate, service: LinkServiceDep, _: AdminApiDep
) -> Link:
    return await service.create_link(payload.target_url, payload.slug)


@router.get("/{slug}", response_model=LinkRead)
async def get_link(slug: str, service: LinkServiceDep, _: AdminApiDep) -> Link:
    link = await service.get_link(slug)
    if link is None:
        raise _not_found()
    return link


@router.patch("/{slug}", response_model=LinkRead)
async def update_link(
    slug: str, payload: LinkUpdate, service: LinkServiceDep, _: AdminApiDep
) -> Link:
    link = await service.update_link(
        slug,
        target_url=payload.target_url,
        is_active=payload.is_active,
    )
    if link is None:
        raise _not_found()
    return link
