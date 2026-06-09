import pytest

from src.domain.entities.task import TaskAggregate
from src.domain.events.task_events import TaskStatusChangedEvent
from src.domain.exceptions import EmptyTitleError
from src.domain.exceptions import InvalidTaskStatusError
from src.domain.value_objects import TaskStatusEnum


def test_create_task_defaults_to_new_status() -> None:
    task = TaskAggregate.create(user_id=1, title="Write tests")

    assert task.status == TaskStatusEnum.NEW
    assert task.id is None
    assert task.description is None


def test_create_task_raises_on_blank_title() -> None:
    with pytest.raises(EmptyTitleError):
        TaskAggregate.create(user_id=1, title="   ")


def test_change_status_new_to_in_progress() -> None:
    task = TaskAggregate.create(user_id=1, title="Write tests")

    task.change_status(TaskStatusEnum.IN_PROGRESS)

    assert task.status == TaskStatusEnum.IN_PROGRESS


def test_change_status_from_terminal_state_raises() -> None:
    task = TaskAggregate.create(user_id=1, title="Write tests")
    task.change_status(TaskStatusEnum.IN_PROGRESS)
    task.change_status(TaskStatusEnum.DONE)

    with pytest.raises(InvalidTaskStatusError):
        task.change_status(TaskStatusEnum.NEW)


def test_change_status_emits_event_with_correct_statuses() -> None:
    task = TaskAggregate.create(user_id=1, title="Write tests")
    task.pull_domain_events()

    task.change_status(TaskStatusEnum.IN_PROGRESS)

    events = task.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], TaskStatusChangedEvent)
    assert events[0].old_status == TaskStatusEnum.NEW
    assert events[0].new_status == TaskStatusEnum.IN_PROGRESS
