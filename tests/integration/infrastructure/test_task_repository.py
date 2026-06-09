import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.task import TaskAggregate
from src.domain.entities.user import UserAggregate
from src.domain.value_objects import TaskStatusEnum
from src.infrastructure.repositories.task_repository import TaskRepository
from src.infrastructure.repositories.user_repository import UserRepository


@pytest.fixture
def user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)


@pytest.fixture
def task_repo(db_session: AsyncSession) -> TaskRepository:
    return TaskRepository(db_session)


async def _make_user(repo: UserRepository, email: str = "user@example.com") -> UserAggregate:
    user = UserAggregate.create(email=email, name="Test User")
    await repo.add(user)
    return user


async def test_add_task_and_get_by_id(
    user_repo: UserRepository,
    task_repo: TaskRepository,
) -> None:
    user = await _make_user(user_repo)
    assert user.id is not None
    task = TaskAggregate.create(user_id=user.id, title="Write docs", description="API docs")

    await task_repo.add(task)

    assert task.id is not None
    found = await task_repo.get_by_id(task.id)
    assert found is not None
    assert found.title == "Write docs"
    assert found.description == "API docs"
    assert found.status == TaskStatusEnum.NEW


async def test_get_by_user_id_filters_and_paginates(
    user_repo: UserRepository,
    task_repo: TaskRepository,
) -> None:
    user = await _make_user(user_repo, "filter@example.com")
    assert user.id is not None

    for title in ("T1", "T2", "T3"):
        await task_repo.add(TaskAggregate.create(user_id=user.id, title=title))

    all_tasks = await task_repo.get_by_user_id(user_id=user.id, status=None, limit=10, offset=0)
    assert len(all_tasks) == 3

    by_status = await task_repo.get_by_user_id(
        user_id=user.id, status=TaskStatusEnum.NEW, limit=10, offset=0
    )
    assert len(by_status) == 3

    no_done = await task_repo.get_by_user_id(
        user_id=user.id, status=TaskStatusEnum.DONE, limit=10, offset=0
    )
    assert len(no_done) == 0

    paginated = await task_repo.get_by_user_id(user_id=user.id, status=None, limit=2, offset=0)
    assert len(paginated) == 2


async def test_delete_removes_task(
    user_repo: UserRepository,
    task_repo: TaskRepository,
) -> None:
    user = await _make_user(user_repo, "delete@example.com")
    assert user.id is not None
    task = TaskAggregate.create(user_id=user.id, title="To delete")
    await task_repo.add(task)
    assert task.id is not None

    await task_repo.delete(task.id)

    assert await task_repo.get_by_id(task.id) is None


async def test_get_stats_returns_correct_counts(
    user_repo: UserRepository,
    task_repo: TaskRepository,
) -> None:
    user = await _make_user(user_repo, "stats@example.com")
    assert user.id is not None

    for title in ("T1", "T2", "T3"):
        await task_repo.add(TaskAggregate.create(user_id=user.id, title=title))

    stats = await task_repo.get_stats_by_user(user.id)

    assert stats.total == 3
    assert stats.new == 3
    assert stats.in_progress == 0
    assert stats.done == 0
    assert stats.cancelled == 0
