import pytest

from src.application.commands.create_task import CreateTaskCommand
from src.application.commands.create_user import CreateUserCommand
from src.application.commands.handlers.create_task_handler import CreateTaskHandler
from src.application.commands.handlers.create_user_handler import CreateUserHandler
from src.application.common.exceptions import InvalidCursorError
from src.application.common.exceptions import NotFoundError
from src.application.queries.get_task_stats import GetTaskStatsQuery
from src.application.queries.get_user import GetUserQuery
from src.application.queries.get_user_tasks import GetUserTasksQuery
from src.application.queries.handlers.get_task_stats_handler import GetTaskStatsHandler
from src.application.queries.handlers.get_user_handler import GetUserHandler
from src.application.queries.handlers.get_user_tasks_handler import GetUserTasksHandler
from src.domain.value_objects import TaskStatusEnum
from tests.unit.application.conftest import FakeUnitOfWork


async def test_get_user_returns_correct_data() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="alice@example.com", name="Alice"))

    response = await GetUserHandler(uow).execute(GetUserQuery(user_id=1))

    assert response.id == 1
    assert response.email == "alice@example.com"
    assert response.name == "Alice"


async def test_get_user_raises_not_found() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(NotFoundError):
        await GetUserHandler(uow).execute(GetUserQuery(user_id=999))


async def test_get_user_tasks_returns_all_tasks() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="bob@example.com", name="Bob"))
    for title in ("T1", "T2", "T3"):
        await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title=title))

    response = await GetUserTasksHandler(uow).execute(
        GetUserTasksQuery(user_id=1, status=None, limit=10)
    )

    assert len(response.items) == 3
    assert response.next_cursor is None


async def test_get_user_tasks_paginates_with_cursor() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="page@example.com", name="Page"))
    for title in ("T1", "T2", "T3"):
        await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title=title))

    first_page = await GetUserTasksHandler(uow).execute(
        GetUserTasksQuery(user_id=1, status=None, limit=2)
    )

    assert len(first_page.items) == 2
    assert first_page.next_cursor is not None

    second_page = await GetUserTasksHandler(uow).execute(
        GetUserTasksQuery(user_id=1, status=None, limit=2, cursor=first_page.next_cursor)
    )

    assert len(second_page.items) == 1
    assert second_page.next_cursor is None

    first_ids = {t.id for t in first_page.items}
    second_ids = {t.id for t in second_page.items}
    assert first_ids.isdisjoint(second_ids)


async def test_get_user_tasks_invalid_cursor_raises() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="bad@example.com", name="Bad"))

    with pytest.raises(InvalidCursorError):
        await GetUserTasksHandler(uow).execute(
            GetUserTasksQuery(user_id=1, status=None, limit=10, cursor="not-a-cursor")
        )


async def test_get_user_tasks_filters_by_status() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="carol@example.com", name="Carol"))
    await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title="New"))
    await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title="Done"))

    response = await GetUserTasksHandler(uow).execute(
        GetUserTasksQuery(user_id=1, status=TaskStatusEnum.DONE, limit=10)
    )

    assert len(response.items) == 0
    assert response.next_cursor is None


async def test_get_user_tasks_raises_not_found_for_missing_user() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(NotFoundError):
        await GetUserTasksHandler(uow).execute(
            GetUserTasksQuery(user_id=777, status=None, limit=10)
        )


async def test_get_task_stats_returns_correct_counts() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="dave@example.com", name="Dave"))
    for _ in range(3):
        await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title="T"))

    stats = await GetTaskStatsHandler(uow).execute(GetTaskStatsQuery(user_id=1))

    assert stats.total == 3
    assert stats.new == 3
    assert stats.in_progress == 0
    assert stats.done == 0
    assert stats.cancelled == 0
