from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from src.infrastructure.di.container import create_container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    container = app.state.dishka_container
    engine = await container.get(AsyncEngine)
    await engine.dispose()
    await container.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Task Manager API",
        description="Backend service for user task management",
        version="0.1.0",
        lifespan=lifespan,
    )

    container = create_container()
    setup_dishka(container=container, app=app)

    return app


app = create_app()
