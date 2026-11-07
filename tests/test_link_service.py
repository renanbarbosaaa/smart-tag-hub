from collections.abc import Iterator

import pytest

from domain.exceptions import SlugAlreadyExistsError, SlugGenerationError
from domain.models import Link
from domain.services import MAX_SLUG_ATTEMPTS, LinkService
from domain.slug import SLUG_LENGTH, generate_slug
from domain.validators import is_valid_slug

TARGET = "https://www.linkedin.com/in/renanbarbosaaa"


class InMemoryLinkRepository:
    def __init__(self) -> None:
        self.links: dict[str, str] = {}

    async def add(self, link: Link) -> Link:
        if link.slug in self.links:
            raise SlugAlreadyExistsError(link.slug)
        self.links[link.slug] = link.target_url
        return link

    async def get_target_url(self, slug: str) -> str | None:
        return self.links.get(slug)

    async def get_by_slug(self, slug: str) -> Link | None:
        target_url = self.links.get(slug)
        return Link(slug=slug, target_url=target_url) if target_url else None

    async def list_links(self, query: str | None = None) -> list[Link]:
        return [
            Link(slug=slug, target_url=target_url)
            for slug, target_url in self.links.items()
            if not query or query in slug or query in target_url
        ]

    async def save(self, link: Link) -> Link | None:
        if link.slug not in self.links:
            return None
        self.links[link.slug] = link.target_url
        return link


def factory_from(slugs: list[str]) -> Iterator[str]:
    return iter(slugs)


def test_generate_slug_is_valid_and_has_fixed_length() -> None:
    slug = generate_slug()

    assert len(slug) == SLUG_LENGTH
    assert is_valid_slug(slug)


async def test_service_retries_on_slug_collision() -> None:
    repo = InMemoryLinkRepository()
    repo.links["aaaaaa"] = "https://existing.com/x"
    slugs = factory_from(["aaaaaa", "aaaaaa", "bbbbbb"])
    service = LinkService(repo, slug_factory=lambda: next(slugs))

    link = await service.create_link(TARGET)

    assert link.slug == "bbbbbb"


async def test_service_gives_up_after_max_attempts() -> None:
    repo = InMemoryLinkRepository()
    repo.links["aaaaaa"] = "https://existing.com/x"
    service = LinkService(repo, slug_factory=lambda: "aaaaaa")

    with pytest.raises(SlugGenerationError):
        await service.create_link(TARGET)
    assert MAX_SLUG_ATTEMPTS > 1


async def test_service_updates_target_url() -> None:
    repo = InMemoryLinkRepository()
    service = LinkService(repo)
    await service.create_link(TARGET, "abc123")

    updated = await service.update_link("abc123", target_url="https://example.com/novo")

    assert updated is not None
    assert updated.target_url == "https://example.com/novo"
    assert repo.links["abc123"] == "https://example.com/novo"


async def test_service_returns_none_when_updating_unknown_link() -> None:
    service = LinkService(InMemoryLinkRepository())

    assert await service.update_link("abc123", target_url=TARGET) is None
