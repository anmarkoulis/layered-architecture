from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from layered_architecture.config.settings import settings

async_session = sessionmaker(  # type: ignore[call-overload]
    create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=50,
        max_overflow=100,
        pool_timeout=30,
        pool_recycle=1800,
        pool_use_lifo=True,
    ),
    expire_on_commit=False,
    class_=AsyncSession,
)


class AsyncDBContextManager:
    def __init__(self) -> None:
        session = sessionmaker(  # type: ignore[call-overload]
            create_async_engine(settings.DATABASE_URL, pool_pre_ping=True),
            expire_on_commit=False,
            class_=AsyncSession,
        )
        self.db = session()

    async def __aenter__(self) -> Any:
        return self.db

    async def __aexit__(self, *exc: Any) -> Any:
        await self.db.close()
