from collections.abc import Callable

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
        if not is_valid_url(target_url):
            raise InvalidUrlError("URL de destino inválida")

        if slug is not None:
            if not is_valid_slug(slug):
                raise InvalidSlugError("Slug deve ter exatamente 6 caracteres alfanuméricos")
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