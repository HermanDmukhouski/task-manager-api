import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import UserAggregate
from src.domain.exceptions import DuplicateEmailError
from src.domain.value_objects import EmailValueObject
from src.infrastructure.repositories.user_repository import UserRepository


@pytest.fixture
def user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)


async def test_add_user_and_get_by_id(
    user_repo: UserRepository,
) -> None:
    user = UserAggregate.create(email="alice@example.com", name="Alice")

    await user_repo.add(user)

    assert user.id is not None
    found = await user_repo.get_by_id(user.id)
    assert found is not None
    assert found.email.value == "alice@example.com"
    assert found.name == "Alice"


async def test_get_by_email_returns_correct_user(
    user_repo: UserRepository,
) -> None:
    user = UserAggregate.create(email="bob@example.com", name="Bob")
    await user_repo.add(user)

    found = await user_repo.get_by_email(EmailValueObject(value="bob@example.com"))

    assert found is not None
    assert found.name == "Bob"


async def test_exists_by_email_true_after_add(
    user_repo: UserRepository,
) -> None:
    user = UserAggregate.create(email="carol@example.com", name="Carol")
    await user_repo.add(user)

    exists = await user_repo.exists_by_email(EmailValueObject(value="carol@example.com"))

    assert exists is True


async def test_exists_by_email_false_for_unknown(
    user_repo: UserRepository,
) -> None:
    exists = await user_repo.exists_by_email(EmailValueObject(value="ghost@example.com"))

    assert exists is False


async def test_add_duplicate_email_raises_domain_error(
    db_session: AsyncSession,
    user_repo: UserRepository,
) -> None:
    user_a = UserAggregate.create(email="dave@example.com", name="Dave")
    await user_repo.add(user_a)

    user_b = UserAggregate.create(email="dave@example.com", name="Dave II")
    with pytest.raises(DuplicateEmailError):
        await user_repo.add(user_b)
