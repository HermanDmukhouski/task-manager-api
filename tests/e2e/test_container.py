import pytest
from dishka import AsyncContainer

from src.application.commands.create_user import CreateUserCommand
from src.application.commands.handlers.create_task_handler import CreateTaskHandler
from src.application.commands.handlers.create_user_handler import CreateUserHandler
from src.application.commands.handlers.delete_task_handler import DeleteTaskHandler
from src.application.common.exceptions import NotFoundError
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.application.queries.get_user import GetUserQuery
from src.application.queries.handlers.get_task_stats_handler import GetTaskStatsHandler
from src.application.queries.handlers.get_user_handler import GetUserHandler
from src.application.queries.handlers.get_user_tasks_handler import GetUserTasksHandler
from src.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork


async def test_container_resolves_unit_of_work(container: AsyncContainer) -> None:
    async with container() as request_container:
        uow = await request_container.get(IUnitOfWork)

    assert isinstance(uow, SQLAlchemyUnitOfWork)


async def test_container_resolves_all_handlers(container: AsyncContainer) -> None:
    handler_types = [
        CreateUserHandler,
        CreateTaskHandler,
        DeleteTaskHandler,
        GetUserHandler,
        GetUserTasksHandler,
        GetTaskStatsHandler,
    ]
    async with container() as request_container:
        for handler_type in handler_types:
            handler = await request_container.get(handler_type)
            assert isinstance(handler, handler_type), f"Failed to resolve {handler_type.__name__}"


async def test_create_user_through_container_writes_to_db(container: AsyncContainer) -> None:
    async with container() as request_container:
        handler = await request_container.get(CreateUserHandler)
        result = await handler.execute(
            CreateUserCommand(email="e2e_container@example.com", name="E2E User")
        )

    assert result.user_id > 0

    async with container() as request_container:
        get_handler = await request_container.get(GetUserHandler)
        user = await get_handler.execute(GetUserQuery(user_id=result.user_id))

    assert user.email == "e2e_container@example.com"
    assert user.name == "E2E User"


async def test_request_scoped_uow_is_separate_per_request(
    container: AsyncContainer,
) -> None:
    async with container() as req1:
        uow1 = await req1.get(IUnitOfWork)

    async with container() as req2:
        uow2 = await req2.get(IUnitOfWork)

    assert uow1 is not uow2


async def test_not_found_error_propagates_through_container(
    container: AsyncContainer,
) -> None:
    async with container() as request_container:
        handler = await request_container.get(GetUserHandler)

        with pytest.raises(NotFoundError):
            await handler.execute(GetUserQuery(user_id=999999))
