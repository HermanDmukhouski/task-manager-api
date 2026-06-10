from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter
from fastapi import Query

from src.application.commands.create_user import CreateUserCommand
from src.application.commands.handlers.create_user_handler import CreateUserHandler
from src.application.queries.get_task_stats import GetTaskStatsQuery
from src.application.queries.get_user import GetUserQuery
from src.application.queries.get_user_tasks import GetUserTasksQuery
from src.application.queries.handlers.get_task_stats_handler import GetTaskStatsHandler
from src.application.queries.handlers.get_user_handler import GetUserHandler
from src.application.queries.handlers.get_user_tasks_handler import GetUserTasksHandler
from src.domain.value_objects import TaskStatusEnum
from src.interfaces.api.schemas import TaskListResponse
from src.interfaces.api.schemas import TaskResponse
from src.interfaces.api.schemas import TaskStatsResponse
from src.interfaces.api.schemas import UserCreateRequest
from src.interfaces.api.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)


@router.post("", status_code=201)
async def create_user(
    body: UserCreateRequest,
    create_handler: FromDishka[CreateUserHandler],
    get_handler: FromDishka[GetUserHandler],
) -> UserResponse:
    result = await create_handler.execute(CreateUserCommand(email=body.email, name=body.name))
    user = await get_handler.execute(GetUserQuery(user_id=result.user_id))
    return UserResponse.model_validate(user)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    handler: FromDishka[GetUserHandler],
) -> UserResponse:
    user = await handler.execute(GetUserQuery(user_id=user_id))
    return UserResponse.model_validate(user)


@router.get("/{user_id}/tasks/stats")
async def get_user_task_stats(
    user_id: int,
    handler: FromDishka[GetTaskStatsHandler],
) -> TaskStatsResponse:
    stats = await handler.execute(GetTaskStatsQuery(user_id=user_id))
    return TaskStatsResponse.model_validate(stats)


@router.get("/{user_id}/tasks")
async def get_user_tasks(
    user_id: int,
    handler: FromDishka[GetUserTasksHandler],
    status: TaskStatusEnum = Query(default=None, description="Filter by task status"),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str = Query(default=None, description="Paste cursor from next_cursor"),
) -> TaskListResponse:
    result = await handler.execute(
        GetUserTasksQuery(
            user_id=user_id,
            status=status,
            limit=limit,
            cursor=cursor,
        )
    )
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in result.items],
        next_cursor=result.next_cursor,
    )
