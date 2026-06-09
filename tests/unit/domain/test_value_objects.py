import pytest

from src.domain.exceptions import InvalidEmailError
from src.domain.value_objects import EmailValueObject
from src.domain.value_objects import TaskStatusEnum


def test_email_value_object_accepts_valid_email() -> None:
    vo = EmailValueObject.create("user@example.com")

    assert vo.value == "user@example.com"


def test_email_value_object_normalizes_to_lowercase() -> None:
    vo = EmailValueObject.create("User@Example.COM")

    assert vo.value == "user@example.com"


def test_email_value_object_raises_on_invalid_format() -> None:
    with pytest.raises(InvalidEmailError):
        EmailValueObject.create("not-an-email")


def test_email_value_objects_are_equal_when_normalized_value_matches() -> None:
    vo1 = EmailValueObject.create("user@example.com")
    vo2 = EmailValueObject.create("USER@EXAMPLE.COM")

    assert vo1 == vo2


def test_task_status_enum_values_are_correct_strings() -> None:
    assert TaskStatusEnum.NEW == "new"
    assert TaskStatusEnum.IN_PROGRESS == "in_progress"
    assert TaskStatusEnum.DONE == "done"
    assert TaskStatusEnum.CANCELLED == "cancelled"
