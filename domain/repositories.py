from typing import Protocol

from domain.models import Link


class LinkRepository(Protocol):
    async def add(self, link: Link) -> Link:
        """Persists the link. Raises SlugAlreadyExistsError on slug collision."""
        ...

    async def get_target_url(self, slug: str) -> str | None: ...