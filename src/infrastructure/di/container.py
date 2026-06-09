from collections.abc import AsyncIterator

from dishka import AsyncContainer
from dishka import Provider
from dishka import Scope
from dishka import make_async_container
from dishka import provide
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.application.commands.handlers.change_task_status_handler import ChangeTaskStatusHandler
from src.application.commands.handlers.create_task_handler import CreateTaskHandler
from src.application.commands.handlers.create_user_handler import CreateUserHandler
from src.application.commands.handlers.delete_task_handler import DeleteTaskHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.application.queries.handlers.get_task_handler import GetTaskHandler
from src.application.queries.handlers.get_task_stats_handler import GetTaskStatsHandler
from src.application.queries.handlers.get_user_handler import GetUserHandler
from src.application.queries.handlers.get_user_tasks_handler import GetUserTasksHandler
from src.config import settings
from src.infrastructure.db.database import create_session_factory
from src.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork


class AppProvider(Provider):
    def __init__(self, database_url: str | None = None) -> None:
        super().__init__()
        self._database_url = database_url or settings.database_url

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            self._database_url,
            echo=settings.environment == "local",
            pool_pre_ping=True,
        )

    @provide(scope=Scope.APP)
    def get_session_factory(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(self, session: AsyncSession) -> IUnitOfWork:
        return SQLAlchemyUnitOfWork(session)

    @provide(scope=Scope.REQUEST)
    def get_create_user_handler(self, uow: IUnitOfWork) -> CreateUserHandler:
        return CreateUserHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_create_task_handler(self, uow: IUnitOfWork) -> CreateTaskHandler:
        return CreateTaskHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_change_task_status_handler(self, uow: IUnitOfWork) -> ChangeTaskStatusHandler:
        return ChangeTaskStatusHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_delete_task_handler(self, uow: IUnitOfWork) -> DeleteTaskHandler:
        return DeleteTaskHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_get_task_handler(self, uow: IUnitOfWork) -> GetTaskHandler:
        return GetTaskHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_get_user_handler(self, uow: IUnitOfWork) -> GetUserHandler:
        return GetUserHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_get_user_tasks_handler(self, uow: IUnitOfWork) -> GetUserTasksHandler:
        return GetUserTasksHandler(uow)

    @provide(scope=Scope.REQUEST)
    def get_get_task_stats_handler(self, uow: IUnitOfWork) -> GetTaskStatsHandler:
        return GetTaskStatsHandler(uow)


def create_container(database_url: str | None = None) -> AsyncContainer:
    return make_async_container(AppProvider(database_url=database_url))
