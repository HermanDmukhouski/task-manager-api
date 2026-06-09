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


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    body: UserCreateRequest,
    create_handler: FromDishka[CreateUserHandler],
    get_handler: FromDishka[GetUserHandler],
) -> UserResponse:
    result = await create_handler.execute(CreateUserCommand(email=body.email, name=body.name))
    user = await get_handler.execute(GetUserQuery(user_id=result.user_id))
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    handler: FromDishka[GetUserHandler],
) -> UserResponse:
    user = await handler.execute(GetUserQuery(user_id=user_id))
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
    )


@router.get("/{user_id}/tasks/stats", response_model=TaskStatsResponse)
async def get_user_task_stats(
    user_id: int,
    handler: FromDishka[GetTaskStatsHandler],
) -> TaskStatsResponse:
    stats = await handler.execute(GetTaskStatsQuery(user_id=user_id))
    return TaskStatsResponse(
        total=stats.total,
        new=stats.new,
        in_progress=stats.in_progress,
        done=stats.done,
        cancelled=stats.cancelled,
    )


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def get_user_tasks(
    user_id: int,
    handler: FromDishka[GetUserTasksHandler],
    status: TaskStatusEnum | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TaskListResponse:
    result = await handler.execute(
        GetUserTasksQuery(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )
    )
    return TaskListResponse(
        items=[
            TaskResponse(
                id=t.id,
                user_id=t.user_id,
                title=t.title,
                description=t.description,
                status=t.status,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in result.items
        ],
        total=result.total,
    )
