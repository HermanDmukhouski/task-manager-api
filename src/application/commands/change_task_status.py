from dataclasses import dataclass

from src.application.common.interfaces import Command
from src.domain.value_objects import TaskStatusEnum


@dataclass(frozen=True)
class ChangeTaskStatusCommand(Command):
    task_id: int
    new_status: TaskStatusEnum
