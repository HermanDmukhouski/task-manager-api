from abc import ABC
from abc import abstractmethod
from typing import NamedTuple

from src.domain.entities.task import TaskAggregate
from src.domain.entities.user import UserAggregate
from src.domain.value_objects import EmailValueObject
from src.domain.value_objects import TaskStatusEnum


class TaskStats(NamedTuple):
    total: int
    new: int
    in_progress: int
    done: int
    cancelled: int


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: UserAggregate) -> None: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserAggregate | None: ...

    @abstractmethod
    async def get_by_email(self, email: EmailValueObject) -> UserAggregate | None: ...

    @abstractmethod
    async def exists_by_email(self, email: EmailValueObject) -> bool: ...


class ITaskRepository(ABC):
    @abstractmethod
    async def add(self, task: TaskAggregate) -> None: ...

    @abstractmethod
    async def get_by_id(self, task_id: int) -> TaskAggregate | None: ...

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
        status: TaskStatusEnum | None,
        limit: int,
        offset: int,
    ) -> list[TaskAggregate]: ...

    @abstractmethod
    async def count_by_user_id(
        self,
        user_id: int,
        status: TaskStatusEnum | None,
    ) -> int: ...

    @abstractmethod
    async def delete(self, task_id: int) -> None: ...

    @abstractmethod
    async def get_stats_by_user(self, user_id: int) -> TaskStats: ...
