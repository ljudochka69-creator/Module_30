import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_recipes.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
async def setup_test_db():
    print("Creating test database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Test database created")
    yield
    if os.path.exists("./test_recipes.db"):
        print("Removing test database")
        os.remove("./test_recipes.db")


@pytest.fixture
async def client(setup_test_db):
    import app.main as main_module

    original_get_session = main_module.get_session

    try:

        async def mock_get_session():
            async with TestSessionLocal() as session:
                yield session

        main_module.get_session = mock_get_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
    finally:
        main_module.get_session = original_get_session


@pytest.fixture
async def db_session(setup_test_db):
    async with TestSessionLocal() as session:
        yield session
