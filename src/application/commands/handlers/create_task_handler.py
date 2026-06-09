from src.application.commands.create_task import CreateTaskCommand
from src.application.commands.create_task import CreateTaskResult
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import CommandHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.domain.entities.task import TaskAggregate


class CreateTaskHandler(CommandHandler[CreateTaskCommand, CreateTaskResult]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateTaskCommand) -> CreateTaskResult:
        async with self._uow:
            user = await self._uow.users.get_by_id(command.user_id)
            if user is None:
                raise NotFoundError(f"User {command.user_id} not found")

            task = TaskAggregate.create(
                user_id=command.user_id,
                title=command.title,
                description=command.description,
            )
            await self._uow.tasks.add(task)
            await self._uow.commit()

        assert task.id is not None
        return CreateTaskResult(task_id=task.id)
