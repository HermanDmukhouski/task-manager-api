import asyncio
from collections.abc import AsyncIterator
from collections.abc import Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.infrastructure.db.models import Base
from src.infrastructure.di.container import create_container


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    async def _create() -> None:
        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    async def _drop() -> None:
        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(_create())
    yield
    asyncio.run(_drop())


@pytest_asyncio.fixture
async def container() -> AsyncIterator[AsyncContainer]:
    c = create_container(database_url=settings.database_url)
    yield c
    await c.close()
