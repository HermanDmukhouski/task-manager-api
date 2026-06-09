from dataclasses import dataclass

from src.application.common.interfaces import Command


@dataclass(frozen=True)
class CreateTaskCommand(Command):
    user_id: int
    title: str
    description: str | None = None


@dataclass(frozen=True)
class CreateTaskResult:
    task_id: int
