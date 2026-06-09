from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime

from src.domain.entities.base import AggregateRoot
from src.domain.events.task_events import TaskCreatedEvent
from src.domain.events.task_events import TaskStatusChangedEvent
from src.domain.exceptions import EmptyTitleError
from src.domain.exceptions import InvalidTaskStatusError
from src.domain.value_objects import TaskStatusEnum

_ALLOWED_TRANSITIONS: dict[TaskStatusEnum, frozenset[TaskStatusEnum]] = {
    TaskStatusEnum.NEW: frozenset({TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.CANCELLED}),
    TaskStatusEnum.IN_PROGRESS: frozenset(
        {TaskStatusEnum.DONE, TaskStatusEnum.CANCELLED, TaskStatusEnum.NEW}
    ),
    TaskStatusEnum.DONE: frozenset(),
    TaskStatusEnum.CANCELLED: frozenset(),
}


@dataclass
class TaskAggregate(AggregateRoot):
    user_id: int
    title: str
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime
    description: str | None = field(default=None)
    id: int | None = field(default=None)

    @classmethod
    def create(
        cls,
        user_id: int,
        title: str,
        description: str | None = None,
    ) -> "TaskAggregate":
        stripped_title = title.strip()
        if not stripped_title:
            raise EmptyTitleError("Title cannot be empty")
        now = datetime.now(UTC)
        task = cls(
            user_id=user_id,
            title=stripped_title,
            description=description,
            status=TaskStatusEnum.NEW,
            created_at=now,
            updated_at=now,
        )
        task._record_event(TaskCreatedEvent(user_id=user_id, title=stripped_title))
        return task

    def change_status(self, new_status: TaskStatusEnum) -> None:
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise InvalidTaskStatusError(
                f"Cannot transition from {self.status!r} to {new_status!r}"
            )
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(UTC)
        self._record_event(
            TaskStatusChangedEvent(
                task_id=self.id,
                user_id=self.user_id,
                old_status=old_status,
                new_status=new_status,
            )
        )

    def update_title(self, title: str) -> None:
        stripped = title.strip()
        if not stripped:
            raise EmptyTitleError("Title cannot be empty")
        self.title = stripped
        self.updated_at = datetime.now(UTC)

    def update_description(self, description: str | None) -> None:
        self.description = description
        self.updated_at = datetime.now(UTC)
