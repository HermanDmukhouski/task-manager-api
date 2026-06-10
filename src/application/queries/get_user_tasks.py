from dataclasses import dataclass
from dataclasses import field

from src.application.common.interfaces import Query
from src.domain.value_objects import TaskStatusEnum


@dataclass(frozen=True)
class GetUserTasksQuery(Query):
    user_id: int
    status: TaskStatusEnum | None = field(default=None)
    limit: int = field(default=20)
    cursor: str | None = field(default=None)
