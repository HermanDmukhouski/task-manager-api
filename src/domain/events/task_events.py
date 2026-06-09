from dataclasses import dataclass

from src.domain.events.base import DomainEvent
from src.domain.value_objects import TaskStatusEnum


@dataclass(frozen=True)
class TaskCreatedEvent(DomainEvent):
    user_id: int
    title: str
    task_id: int | None = None


@dataclass(frozen=True)
class TaskStatusChangedEvent(DomainEvent):
    user_id: int
    old_status: TaskStatusEnum
    new_status: TaskStatusEnum
    task_id: int | None = None
