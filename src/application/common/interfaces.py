from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

TCommand = TypeVar("TCommand")
TQuery = TypeVar("TQuery")
TResult = TypeVar("TResult")


@dataclass(frozen=True)
class Command:
    pass


@dataclass(frozen=True)
class Query:
    pass


class CommandHandler(ABC, Generic[TCommand, TResult]):
    @abstractmethod
    async def execute(self, command: TCommand) -> TResult: ...


class QueryHandler(ABC, Generic[TQuery, TResult]):
    @abstractmethod
    async def execute(self, query: TQuery) -> TResult: ...
