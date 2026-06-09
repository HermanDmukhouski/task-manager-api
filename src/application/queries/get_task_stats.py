from dataclasses import dataclass

from src.application.common.interfaces import Query


@dataclass(frozen=True)
class GetTaskStatsQuery(Query):
    user_id: int
