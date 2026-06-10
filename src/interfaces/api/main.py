import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

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
    # Контейнер сам закрывает APP-scope ресурсы, включая dispose() движка БД.
    await app.state.dishka_container.close()


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
