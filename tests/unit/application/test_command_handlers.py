import pytest

from src.application.commands.change_task_status import ChangeTaskStatusCommand
from src.application.commands.create_task import CreateTaskCommand
from src.application.commands.create_user import CreateUserCommand
from src.application.commands.delete_task import DeleteTaskCommand
from src.application.commands.handlers.change_task_status_handler import ChangeTaskStatusHandler
from src.application.commands.handlers.create_task_handler import CreateTaskHandler
from src.application.commands.handlers.create_user_handler import CreateUserHandler
from src.application.commands.handlers.delete_task_handler import DeleteTaskHandler
from src.application.common.exceptions import ConflictError
from src.application.common.exceptions import NotFoundError
from src.domain.exceptions import InvalidTaskStatusError
from src.domain.value_objects import TaskStatusEnum
from tests.unit.application.conftest import FakeUnitOfWork


async def test_create_user_returns_user_id() -> None:
    uow = FakeUnitOfWork()
    handler = CreateUserHandler(uow)

    result = await handler.execute(CreateUserCommand(email="alice@example.com", name="Alice"))

    assert result.user_id == 1
    assert uow.committed is True


async def test_create_user_raises_conflict_on_duplicate_email() -> None:
    uow = FakeUnitOfWork()
    handler = CreateUserHandler(uow)
    await handler.execute(CreateUserCommand(email="alice@example.com", name="Alice"))
    uow.committed = False

    with pytest.raises(ConflictError):
        await handler.execute(CreateUserCommand(email="alice@example.com", name="Alice 2"))


async def test_create_task_returns_task_id() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="bob@example.com", name="Bob"))
    uow.committed = False

    result = await CreateTaskHandler(uow).execute(
        CreateTaskCommand(user_id=1, title="Write tests", description="All edge cases")
    )

    assert result.task_id == 1
    assert uow.committed is True


async def test_create_task_raises_not_found_for_missing_user() -> None:
    uow = FakeUnitOfWork()
    handler = CreateTaskHandler(uow)

    with pytest.raises(NotFoundError):
        await handler.execute(CreateTaskCommand(user_id=999, title="Orphan task"))


async def test_change_task_status_updates_status() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="c@example.com", name="C"))
    await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title="Task"))
    uow.committed = False

    await ChangeTaskStatusHandler(uow).execute(
        ChangeTaskStatusCommand(task_id=1, new_status=TaskStatusEnum.IN_PROGRESS)
    )

    task = await uow.tasks.get_by_id(1)
    assert task is not None
    assert task.status == TaskStatusEnum.IN_PROGRESS
    assert uow.committed is True


async def test_change_task_status_raises_not_found() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(NotFoundError):
        await ChangeTaskStatusHandler(uow).execute(
            ChangeTaskStatusCommand(task_id=999, new_status=TaskStatusEnum.DONE)
        )


async def test_change_task_status_raises_on_invalid_transition() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="d@example.com", name="D"))
    await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title="Task"))
    await ChangeTaskStatusHandler(uow).execute(
        ChangeTaskStatusCommand(task_id=1, new_status=TaskStatusEnum.IN_PROGRESS)
    )
    await ChangeTaskStatusHandler(uow).execute(
        ChangeTaskStatusCommand(task_id=1, new_status=TaskStatusEnum.DONE)
    )

    with pytest.raises(InvalidTaskStatusError):
        await ChangeTaskStatusHandler(uow).execute(
            ChangeTaskStatusCommand(task_id=1, new_status=TaskStatusEnum.NEW)
        )


async def test_delete_task_removes_task() -> None:
    uow = FakeUnitOfWork()
    await CreateUserHandler(uow).execute(CreateUserCommand(email="e@example.com", name="E"))
    await CreateTaskHandler(uow).execute(CreateTaskCommand(user_id=1, title="To delete"))
    uow.committed = False

    await DeleteTaskHandler(uow).execute(DeleteTaskCommand(task_id=1))

    assert await uow.tasks.get_by_id(1) is None
    assert uow.committed is True


async def test_delete_task_raises_not_found() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(NotFoundError):
        await DeleteTaskHandler(uow).execute(DeleteTaskCommand(task_id=404))
