from src.application.common.dto import TaskResponse
from src.application.common.dto import UserTasksResponse
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import QueryHandler
from src.application.common.pagination import TaskCursor
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.application.queries.get_user_tasks import GetUserTasksQuery
from src.domain.entities.task import TaskAggregate


def _to_task_response(task: TaskAggregate) -> TaskResponse:
    assert task.id is not None
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


class GetUserTasksHandler(QueryHandler[GetUserTasksQuery, UserTasksResponse]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, query: GetUserTasksQuery) -> UserTasksResponse:
        cursor = TaskCursor.decode(query.cursor) if query.cursor is not None else None

        async with self._uow:
            user = await self._uow.users.get_by_id(query.user_id)
            if user is None:
                raise NotFoundError(f"User {query.user_id} not found")

            # Запрашиваем на один элемент больше, чтобы понять, есть ли следующая страница.
            tasks = await self._uow.tasks.get_by_user_id(
                user_id=query.user_id,
                status=query.status,
                limit=query.limit + 1,
                cursor=cursor,
            )

        has_next = len(tasks) > query.limit
        page = tasks[: query.limit]

        next_cursor: str | None = None
        if has_next and page:
            last = page[-1]
            assert last.id is not None
            next_cursor = TaskCursor(created_at=last.created_at, id=last.id).encode()

        return UserTasksResponse(
            items=[_to_task_response(t) for t in page],
            next_cursor=next_cursor,
        )
