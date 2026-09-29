from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from domain.services import LinkService
from infrastructure.database import get_session
from infrastructure.repositories import SQLAlchemyLinkRepository


def get_link_service(session: Annotated[AsyncSession, Depends(get_session)]) -> LinkService:
    return LinkService(SQLAlchemyLinkRepository(session))


LinkServiceDep = Annotated[LinkService, Depends(get_link_service)]