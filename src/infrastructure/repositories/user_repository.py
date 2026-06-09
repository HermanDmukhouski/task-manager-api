from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories import IUserRepository
from src.domain.entities.user import UserAggregate
from src.domain.exceptions import DuplicateEmailError
from src.domain.value_objects import EmailValueObject
from src.infrastructure.db.models import UserTable
from src.infrastructure.db.models import user_from_domain
from src.infrastructure.db.models import user_to_domain


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: UserAggregate) -> None:
        row = user_from_domain(user)
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise DuplicateEmailError(f"User with email {user.email!r} already exists") from exc
        user.id = row.id

    async def get_by_id(self, user_id: int) -> UserAggregate | None:
        row = await self._session.get(UserTable, user_id)
        if row is None:
            return None
        return user_to_domain(row)

    async def get_by_email(self, email: EmailValueObject) -> UserAggregate | None:
        result = await self._session.execute(
            select(UserTable).where(UserTable.email == email.value)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return user_to_domain(row)

    async def exists_by_email(self, email: EmailValueObject) -> bool:
        result = await self._session.execute(select(exists().where(UserTable.email == email.value)))
        return bool(result.scalar())
