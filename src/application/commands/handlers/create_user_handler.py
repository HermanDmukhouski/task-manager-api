from src.application.commands.create_user import CreateUserCommand
from src.application.commands.create_user import CreateUserResult
from src.application.common.exceptions import ConflictError
from src.application.common.interfaces import CommandHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.domain.entities.user import UserAggregate
from src.domain.exceptions import DuplicateEmailError
from src.domain.value_objects import EmailValueObject


class CreateUserHandler(CommandHandler[CreateUserCommand, CreateUserResult]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateUserCommand) -> CreateUserResult:
        email_vo = EmailValueObject.create(command.email)

        async with self._uow:
            already_exists = await self._uow.users.exists_by_email(email_vo)
            if already_exists:
                raise ConflictError(f"User with email {command.email!r} already exists")

            user = UserAggregate.create(email=command.email, name=command.name)
            try:
                await self._uow.users.add(user)
            except DuplicateEmailError as exc:
                raise ConflictError(str(exc)) from exc

            await self._uow.commit()

        assert user.id is not None
        return CreateUserResult(user_id=user.id)
