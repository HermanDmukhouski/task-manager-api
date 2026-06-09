from src.application.common.dto import TaskStatsResponse
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import QueryHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.application.queries.get_task_stats import GetTaskStatsQuery


class GetTaskStatsHandler(QueryHandler[GetTaskStatsQuery, TaskStatsResponse]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, query: GetTaskStatsQuery) -> TaskStatsResponse:
        async with self._uow:
            user = await self._uow.users.get_by_id(query.user_id)
            if user is None:
                raise NotFoundError(f"User {query.user_id} not found")

            stats = await self._uow.tasks.get_stats_by_user(query.user_id)

        return TaskStatsResponse(
            total=stats.total,
            new=stats.new,
            in_progress=stats.in_progress,
            done=stats.done,
            cancelled=stats.cancelled,
        )
