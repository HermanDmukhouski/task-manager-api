import pytest

from src.domain.entities.user import UserAggregate
from src.domain.events.user_events import UserCreatedEvent
from src.domain.exceptions import EmptyNameError
from src.domain.exceptions import InvalidEmailError


def test_create_user_sets_correct_fields() -> None:
    user = UserAggregate.create(email="alice@example.com", name="Alice")

    assert user.email.value == "alice@example.com"
    assert user.name == "Alice"
    assert user.id is None
    assert user.created_at is not None


def test_create_user_raises_on_invalid_email() -> None:
    with pytest.raises(InvalidEmailError):
        UserAggregate.create(email="not-an-email", name="Alice")


def test_create_user_raises_on_blank_name() -> None:
    with pytest.raises(EmptyNameError):
        UserAggregate.create(email="alice@example.com", name="   ")


def test_create_user_emits_user_created_event() -> None:
    user = UserAggregate.create(email="alice@example.com", name="Alice")

    events = user.pull_domain_events()

    assert len(events) == 1
    assert isinstance(events[0], UserCreatedEvent)
    assert events[0].email == "alice@example.com"
    assert events[0].name == "Alice"


def test_change_name_updates_name_and_clears_whitespace() -> None:
    user = UserAggregate.create(email="alice@example.com", name="Alice")

    user.change_name("  Bob  ")

    assert user.name == "Bob"
