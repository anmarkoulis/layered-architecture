import asyncio
from typing import Any, AsyncGenerator, Generator

import asyncpg
import httpx
import pytest
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from layered_architecture.config.settings import settings
from layered_architecture.db.depends import get_db
from layered_architecture.db.models.base import Base
from layered_architecture.main import app

# Create async engine for tests
engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_database_if_not_exists() -> None:
    """Create test database if it doesn't exist."""
    test_database_url = make_url(settings.TEST_DATABASE_URL)
    try:
        await asyncpg.connect(
            host=test_database_url.host,
            port=test_database_url.port,
            user=test_database_url.username,
            password=test_database_url.password,
            database=test_database_url.database,
        )
    except asyncpg.InvalidCatalogNameError:
        sys_conn = await asyncpg.connect(
            host=test_database_url.host,
            port=test_database_url.port,
            user=test_database_url.username,
            password=test_database_url.password,
            database="template1",
        )
        await sys_conn.execute(f"CREATE DATABASE {test_database_url.database}")
        await sys_conn.close()


@pytest.fixture(scope="function")
async def db_engine() -> Any:
    """Create and configure the test database engine.

    :yield: The test database engine
    :rtype: Any
    """
    await create_database_if_not_exists()
    engine: AsyncEngine = create_async_engine(
        settings.TEST_DATABASE_URL,
        pool_pre_ping=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine


@pytest.fixture(scope="function")
async def db(db_engine: Any) -> AsyncGenerator:
    """Create a test database session.

    :param db_engine: The test database engine
    :type db_engine: Any
    :yield: The test database session
    :rtype: AsyncGenerator
    """
    async_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    AsyncScopedSession = async_scoped_session(
        async_session_factory, scopefunc=lambda: None
    )
    session = AsyncScopedSession()

    try:
        yield session
    finally:
        await session.close()
        await db_engine.dispose()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio backend for testing.

    :return: The anyio backend
    :rtype: str
    """
    return "asyncio"


@pytest.fixture(scope="function")
async def app_with_test_db(db: AsyncSession) -> Any:
    """Override the app fixture to use an in-memory test database.

    :param db: The test database session
    :type db: AsyncSession
    :yield: The test app
    :rtype: Any
    """

    def override_get_db() -> AsyncSession:
        return db

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def seed_test_data(db: AsyncSession) -> AsyncGenerator[None, None]:
    """Seed test data into the database.

    :param db: The test database session
    :type db: AsyncSession
    :yield: None
    :rtype: AsyncGenerator[None, None]
    """
    # Insert pizzas
    await db.execute(
        text(
            """
        INSERT INTO pizza (id, name, description, price, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'Margherita', 'Classic tomato sauce, mozzarella, fresh basil', 12.99, NOW(), NOW()),
            (gen_random_uuid(), 'Pepperoni', 'Tomato sauce, mozzarella, spicy pepperoni', 14.99, NOW(), NOW()),
            (gen_random_uuid(), 'Quattro Formaggi', 'Four cheese blend: mozzarella, gorgonzola, parmesan, ricotta', 16.99, NOW(), NOW()),
            (gen_random_uuid(), 'Prosciutto e Funghi', 'Tomato sauce, mozzarella, prosciutto, mushrooms', 17.99, NOW(), NOW()),
            (gen_random_uuid(), 'Marinara', 'Tomato sauce, garlic, oregano, extra virgin olive oil', 11.99, NOW(), NOW()),
            (gen_random_uuid(), 'Vegetariana', 'Tomato sauce, mozzarella, bell peppers, mushrooms, onions, olives', 15.99, NOW(), NOW()),
            (gen_random_uuid(), 'Diavola', 'Tomato sauce, mozzarella, spicy salami, chili peppers', 15.99, NOW(), NOW()),
            (gen_random_uuid(), 'Capricciosa', 'Tomato sauce, mozzarella, ham, mushrooms, artichokes, olives', 16.99, NOW(), NOW()),
            (gen_random_uuid(), 'Quattro Stagioni', 'Tomato sauce, mozzarella, ham, mushrooms, artichokes, olives, eggs', 17.99, NOW(), NOW()),
            (gen_random_uuid(), 'Napoli', 'Tomato sauce, mozzarella, anchovies, capers, olives', 16.99, NOW(), NOW())
        """
        )
    )

    # Insert beers
    await db.execute(
        text(
            """
        INSERT INTO beer (id, name, brand, price, is_tap, created_at, updated_at)
        VALUES
            -- Bottled Beers
            (gen_random_uuid(), 'Peroni Nastro Azzurro', 'Peroni', 5.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Moretti', 'Birra Moretti', 5.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Corona Extra', 'Corona', 6.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Heineken', 'Heineken', 5.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Stella Artois', 'Stella Artois', 6.49, false, NOW(), NOW()),
            (gen_random_uuid(), 'Guinness Draught', 'Guinness', 7.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Hoegaarden', 'Hoegaarden', 6.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Leffe Blonde', 'Leffe', 7.49, false, NOW(), NOW()),
            (gen_random_uuid(), 'Chimay Blue', 'Chimay', 9.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Duvel', 'Duvel', 8.99, false, NOW(), NOW()),
            -- Tap Beers
            (gen_random_uuid(), 'Pilsner Urquell', 'Pilsner Urquell', 6.99, true, NOW(), NOW()),
            (gen_random_uuid(), 'Kozel Dark', 'Kozel', 7.49, true, NOW(), NOW()),
            (gen_random_uuid(), 'Staropramen', 'Staropramen', 6.49, true, NOW(), NOW()),
            (gen_random_uuid(), 'Budweiser Budvar', 'Budweiser', 6.99, true, NOW(), NOW()),
            (gen_random_uuid(), 'Krombacher', 'Krombacher', 6.49, true, NOW(), NOW())
        """
        )
    )
    await db.commit()
    yield


@pytest.fixture
async def async_client(
    app_with_test_db: Any, seed_test_data: None
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async client for testing.

    :param app_with_test_db: The test app
    :type app_with_test_db: Any
    :param seed_test_data: The seed test data fixture
    :type seed_test_data: None
    :yield: An async client for testing
    :rtype: AsyncGenerator[httpx.AsyncClient, None]
    """
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app_with_test_db),
        base_url="http://test",
    ) as client:
        yield client


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_session dependency for testing.

    :yield: The test session
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with TestingSessionLocal() as session:
        yield session


async def override_get_auth_service() -> None:
    """Override the get_auth_service dependency for testing.

    :return: None
    :rtype: None
    """
    return None


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session.

    :yield: The event loop
    :rtype: Generator
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[None, None]:
    """Create and drop test database tables.

    :yield: None
    :rtype: AsyncGenerator[None, None]
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
