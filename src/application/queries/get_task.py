from dataclasses import dataclass

from src.application.common.interfaces import Query


@dataclass(frozen=True)
class GetTaskQuery(Query):
    task_id: int
