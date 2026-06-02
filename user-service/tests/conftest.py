import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/user_test_db"


@pytest.fixture(autouse=True)
async def prepare_database():
    engine_test = create_async_engine(TEST_DB_URL)
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine_test

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


@pytest.fixture
async def client(prepare_database):
    engine_test = prepare_database
    AsyncSessionTest = sessionmaker(
        engine_test, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with AsyncSessionTest() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()