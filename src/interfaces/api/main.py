import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from src.infrastructure.di.container import create_container
from src.interfaces.api.exception_handlers import register_exception_handlers
from src.interfaces.api.routers.tasks import router as tasks_router
from src.interfaces.api.routers.users import router as users_router
from src.interfaces.middlewares.logging import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


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
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(LoggingMiddleware)

    app.include_router(users_router)
    app.include_router(tasks_router)

    register_exception_handlers(app)

    container = create_container()
    setup_dishka(container=container, app=app)

    return app


app = create_app()
