from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import UserAggregate
from src.infrastructure.db.models import UserTable
from src.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork


async def test_commit_persists_changes(db_session: AsyncSession) -> None:
    uow = SQLAlchemyUnitOfWork(db_session)

    async with uow:
        user = UserAggregate.create(email="commit@example.com", name="Commit Test")
        await uow.users.add(user)
        await uow.commit()

    assert user.id is not None
    row = await db_session.get(UserTable, user.id)
    assert row is not None
    assert row.email == "commit@example.com"


async def test_rollback_discards_changes(db_session: AsyncSession) -> None:
    uow = SQLAlchemyUnitOfWork(db_session)

    async with uow:
        user = UserAggregate.create(email="rollback@example.com", name="Rollback Test")
        await uow.users.add(user)
        await uow.rollback()

    result = await db_session.execute(
        select(UserTable).where(UserTable.email == "rollback@example.com")
    )
    assert result.scalar_one_or_none() is None


async def test_exception_in_context_triggers_rollback(db_session: AsyncSession) -> None:
    import contextlib

    uow = SQLAlchemyUnitOfWork(db_session)

    with contextlib.suppress(ValueError):
        async with uow:
            user = UserAggregate.create(email="exc@example.com", name="Exception Test")
            await uow.users.add(user)
            raise ValueError("simulated error")

    result = await db_session.execute(select(UserTable).where(UserTable.email == "exc@example.com"))
    assert result.scalar_one_or_none() is None
