from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects import TaskStatusEnum


@dataclass(frozen=True)
class UserResponse:
    id: int
    email: str
    name: str
    created_at: datetime


@dataclass(frozen=True)
class TaskResponse:
    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserTasksResponse:
    items: list[TaskResponse]
    next_cursor: str | None


@dataclass(frozen=True)
class TaskStatsResponse:
    total: int
    new: int
    in_progress: int
    done: int
    cancelled: int
