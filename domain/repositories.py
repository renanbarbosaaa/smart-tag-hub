from typing import Protocol

from domain.models import Link


class LinkRepository(Protocol):
    async def add(self, link: Link) -> Link:
        """Persiste o link e levanta SlugAlreadyExistsError em colisões."""
        ...

    async def get_target_url(self, slug: str) -> str | None: ...

    async def get_by_slug(self, slug: str) -> Link | None: ...

    async def list_links(self, query: str | None = None) -> list[Link]: ...

    async def save(self, link: Link) -> Link | None: ...
