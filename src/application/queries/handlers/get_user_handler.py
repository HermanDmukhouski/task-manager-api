from src.application.common.dto import UserResponse
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import QueryHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.application.queries.get_user import GetUserQuery


class GetUserHandler(QueryHandler[GetUserQuery, UserResponse]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, query: GetUserQuery) -> UserResponse:
        async with self._uow:
            user = await self._uow.users.get_by_id(query.user_id)
            if user is None:
                raise NotFoundError(f"User {query.user_id} not found")

        assert user.id is not None
        return UserResponse(
            id=user.id,
            email=user.email.value,
            name=user.name,
            created_at=user.created_at,
        )
