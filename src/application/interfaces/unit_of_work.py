from abc import ABC
from abc import abstractmethod
from types import TracebackType
from typing import Self

from src.application.interfaces.repositories import ITaskRepository
from src.application.interfaces.repositories import IUserRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def users(self) -> IUserRepository: ...

    @property
    @abstractmethod
    def tasks(self) -> ITaskRepository: ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
