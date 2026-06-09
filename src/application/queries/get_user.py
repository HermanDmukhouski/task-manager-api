from dataclasses import dataclass

from src.application.common.interfaces import Query


@dataclass(frozen=True)
class GetUserQuery(Query):
    user_id: int
