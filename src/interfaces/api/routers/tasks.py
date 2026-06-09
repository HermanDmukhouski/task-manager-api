from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka
from fastapi import APIRouter

from src.application.commands.change_task_status import ChangeTaskStatusCommand
from src.application.commands.create_task import CreateTaskCommand
from src.application.commands.delete_task import DeleteTaskCommand
from src.application.commands.handlers.change_task_status_handler import ChangeTaskStatusHandler
from src.application.commands.handlers.create_task_handler import CreateTaskHandler
from src.application.commands.handlers.delete_task_handler import DeleteTaskHandler
from src.application.queries.get_task import GetTaskQuery
from src.application.queries.handlers.get_task_handler import GetTaskHandler
from src.interfaces.api.schemas import DeletedResponse
from src.interfaces.api.schemas import TaskCreateRequest
from src.interfaces.api.schemas import TaskResponse
from src.interfaces.api.schemas import TaskStatusUpdateRequest

router = APIRouter(tags=["tasks"], route_class=DishkaRoute)


@router.post("/users/{user_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: int,
    body: TaskCreateRequest,
    create_handler: FromDishka[CreateTaskHandler],
    get_handler: FromDishka[GetTaskHandler],
) -> TaskResponse:
    result = await create_handler.execute(
        CreateTaskCommand(
            user_id=user_id,
            title=body.title,
            description=body.description,
        )
    )
    task = await get_handler.execute(GetTaskQuery(task_id=result.task_id))
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    body: TaskStatusUpdateRequest,
    change_handler: FromDishka[ChangeTaskStatusHandler],
    get_handler: FromDishka[GetTaskHandler],
) -> TaskResponse:
    await change_handler.execute(ChangeTaskStatusCommand(task_id=task_id, new_status=body.status))
    task = await get_handler.execute(GetTaskQuery(task_id=task_id))
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.delete("/tasks/{task_id}", response_model=DeletedResponse)
async def delete_task(
    task_id: int,
    handler: FromDishka[DeleteTaskHandler],
) -> DeletedResponse:
    await handler.execute(DeleteTaskCommand(task_id=task_id))
    return DeletedResponse()
