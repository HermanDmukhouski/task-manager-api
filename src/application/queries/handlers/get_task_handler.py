from src.application.common.dto import TaskResponse
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import QueryHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.application.queries.get_task import GetTaskQuery


class GetTaskHandler(QueryHandler[GetTaskQuery, TaskResponse]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, query: GetTaskQuery) -> TaskResponse:
        async with self._uow:
            task = await self._uow.tasks.get_by_id(query.task_id)
            if task is None:
                raise NotFoundError(f"Task {query.task_id} not found")

        if task.id is None:
            raise ValueError("Cannot map unpersisted task to response")
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
