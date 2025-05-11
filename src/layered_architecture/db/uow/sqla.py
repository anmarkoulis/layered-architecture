from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseUnitOfWork

logger = getLogger(__name__)


class SQLAUnitOfWork(BaseUnitOfWork):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def rollback(self) -> None:
        logger.debug("Rolling back transaction")
        await self.db.rollback()

    async def commit(self) -> None:
        logger.debug("Commiting transaction")
        await self.db.commit()
