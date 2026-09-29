from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import SlugAlreadyExistsError
from domain.models import Link
from infrastructure.models import LinkModel


class SQLAlchemyLinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, link: Link) -> Link:
        self._session.add(
            LinkModel(
                slug=link.slug,
                target_url=link.target_url,
                created_at=link.created_at,
            )
        )
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise SlugAlreadyExistsError(f"Slug '{link.slug}' já está em uso") from exc
        return link

    async def get_target_url(self, slug: str) -> str | None:
        result = await self._session.execute(
            select(LinkModel.target_url).where(LinkModel.slug == slug)
        )
        return result.scalar_one_or_none()