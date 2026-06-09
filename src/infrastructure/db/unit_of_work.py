from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories import ITaskRepository
from src.application.interfaces.repositories import IUserRepository
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.infrastructure.repositories.task_repository import TaskRepository
from src.infrastructure.repositories.user_repository import UserRepository


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users: UserRepository | None = None
        self._tasks: TaskRepository | None = None

    @property
    def users(self) -> IUserRepository:
        if self._users is None:
            self._users = UserRepository(self._session)
        return self._users

    @property
    def tasks(self) -> ITaskRepository:
        if self._tasks is None:
            self._tasks = TaskRepository(self._session)
        return self._tasks

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
