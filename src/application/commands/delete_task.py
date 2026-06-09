from dataclasses import dataclass

from src.application.common.interfaces import Command


@dataclass(frozen=True)
class DeleteTaskCommand(Command):
    task_id: int
