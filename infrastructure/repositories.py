from sqlalchemy import or_, select
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
                is_active=link.is_active,
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
            select(LinkModel.target_url).where(
                LinkModel.slug == slug,
                LinkModel.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Link | None:
        result = await self._session.execute(
            select(LinkModel).where(LinkModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    async def list_links(self, query: str | None = None) -> list[Link]:
        statement = select(LinkModel).order_by(LinkModel.created_at.desc())
        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                or_(LinkModel.slug.ilike(pattern), LinkModel.target_url.ilike(pattern))
            )
        result = await self._session.execute(statement)
        return [self._to_domain(model) for model in result.scalars().all()]

    async def save(self, link: Link) -> Link | None:
        result = await self._session.execute(
            select(LinkModel).where(LinkModel.slug == link.slug)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.target_url = link.target_url
        model.is_active = link.is_active
        await self._session.commit()
        return link

    @staticmethod
    def _to_domain(model: LinkModel) -> Link:
        return Link(
            slug=model.slug,
            target_url=model.target_url,
            created_at=model.created_at,
            is_active=model.is_active,
        )
