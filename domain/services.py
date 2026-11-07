from collections.abc import Callable
from dataclasses import replace

from domain.exceptions import (
    InvalidSlugError,
    InvalidUrlError,
    SlugAlreadyExistsError,
    SlugGenerationError,
)
from domain.models import Link
from domain.repositories import LinkRepository
from domain.slug import generate_slug
from domain.validators import is_valid_slug, is_valid_url

MAX_SLUG_ATTEMPTS = 5


class LinkService:
    def __init__(
        self,
        repository: LinkRepository,
        slug_factory: Callable[[], str] = generate_slug,
    ) -> None:
        self._repository = repository
        self._slug_factory = slug_factory

    async def create_link(self, target_url: str, slug: str | None = None) -> Link:
        self._validate_target_url(target_url)

        if slug is not None:
            self._validate_slug(slug)
            return await self._repository.add(Link(slug=slug, target_url=target_url))

        for _ in range(MAX_SLUG_ATTEMPTS):
            try:
                return await self._repository.add(
                    Link(slug=self._slug_factory(), target_url=target_url)
                )
            except SlugAlreadyExistsError:
                continue
        raise SlugGenerationError("Não foi possível gerar um slug único")

    async def resolve(self, slug: str) -> str | None:
        return await self._repository.get_target_url(slug)

    async def get_link(self, slug: str) -> Link | None:
        if not is_valid_slug(slug):
            return None
        return await self._repository.get_by_slug(slug)

    async def list_links(self, query: str | None = None) -> list[Link]:
        normalized_query = query.strip() if query else None
        return await self._repository.list_links(normalized_query)

    async def update_link(
        self,
        slug: str,
        *,
        target_url: str | None = None,
        is_active: bool | None = None,
    ) -> Link | None:
        self._validate_slug(slug)
        if target_url is not None:
            self._validate_target_url(target_url)

        link = await self._repository.get_by_slug(slug)
        if link is None:
            return None
        if target_url is None and is_active is None:
            return link

        updated = replace(
            link,
            target_url=target_url if target_url is not None else link.target_url,
            is_active=is_active if is_active is not None else link.is_active,
        )
        return await self._repository.save(updated)

    @staticmethod
    def _validate_slug(slug: str) -> None:
        if not is_valid_slug(slug):
            raise InvalidSlugError(
                "Slug deve ter exatamente 6 caracteres alfanuméricos"
            )

    @staticmethod
    def _validate_target_url(target_url: str) -> None:
        if not is_valid_url(target_url):
            raise InvalidUrlError("URL de destino inválida")
