from types import TracebackType
from typing import Self

from src.application.interfaces.repositories import ITaskRepository
from src.application.interfaces.repositories import IUserRepository
from src.application.interfaces.repositories import TaskStats
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.domain.entities.task import TaskAggregate
from src.domain.entities.user import UserAggregate
from src.domain.value_objects import EmailValueObject
from src.domain.value_objects import TaskStatusEnum


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._store: dict[int, UserAggregate] = {}
        self._next_id = 1

    async def add(self, user: UserAggregate) -> None:
        user.id = self._next_id
        self._store[self._next_id] = user
        self._next_id += 1

    async def get_by_id(self, user_id: int) -> UserAggregate | None:
        return self._store.get(user_id)

    async def get_by_email(self, email: EmailValueObject) -> UserAggregate | None:
        return next(
            (u for u in self._store.values() if u.email == email),
            None,
        )

    async def exists_by_email(self, email: EmailValueObject) -> bool:
        return any(u.email == email for u in self._store.values())


class FakeTaskRepository(ITaskRepository):
    def __init__(self) -> None:
        self._store: dict[int, TaskAggregate] = {}
        self._next_id = 1

    async def add(self, task: TaskAggregate) -> None:
        task.id = self._next_id
        self._store[self._next_id] = task
        self._next_id += 1

    async def get_by_id(self, task_id: int) -> TaskAggregate | None:
        return self._store.get(task_id)

    async def get_by_user_id(
        self,
        user_id: int,
        status: TaskStatusEnum | None,
        limit: int,
        offset: int,
    ) -> list[TaskAggregate]:
        items = [t for t in self._store.values() if t.user_id == user_id]
        if status is not None:
            items = [t for t in items if t.status == status]
        return items[offset : offset + limit]

    async def count_by_user_id(
        self,
        user_id: int,
        status: TaskStatusEnum | None,
    ) -> int:
        items = [t for t in self._store.values() if t.user_id == user_id]
        if status is not None:
            items = [t for t in items if t.status == status]
        return len(items)

    async def update(self, task: TaskAggregate) -> None:
        if task.id is not None:
            self._store[task.id] = task

    async def delete(self, task_id: int) -> None:
        self._store.pop(task_id, None)

    async def get_stats_by_user(self, user_id: int) -> TaskStats:
        tasks = [t for t in self._store.values() if t.user_id == user_id]
        return TaskStats(
            total=len(tasks),
            new=sum(1 for t in tasks if t.status == TaskStatusEnum.NEW),
            in_progress=sum(1 for t in tasks if t.status == TaskStatusEnum.IN_PROGRESS),
            done=sum(1 for t in tasks if t.status == TaskStatusEnum.DONE),
            cancelled=sum(1 for t in tasks if t.status == TaskStatusEnum.CANCELLED),
        )


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self._users = FakeUserRepository()
        self._tasks = FakeTaskRepository()
        self.committed = False

    @property
    def users(self) -> IUserRepository:
        return self._users

    @property
    def tasks(self) -> ITaskRepository:
        return self._tasks

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass
