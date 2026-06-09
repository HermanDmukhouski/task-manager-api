from src.application.commands.change_task_status import ChangeTaskStatusCommand
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import CommandHandler
from src.application.interfaces.unit_of_work import IUnitOfWork
from src.domain.exceptions import InvalidTaskStatusError


class ChangeTaskStatusHandler(CommandHandler[ChangeTaskStatusCommand, None]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: ChangeTaskStatusCommand) -> None:
        async with self._uow:
            task = await self._uow.tasks.get_by_id(command.task_id)
            if task is None:
                raise NotFoundError(f"Task {command.task_id} not found")

            try:
                task.change_status(command.new_status)
            except InvalidTaskStatusError:
                raise

            await self._uow.tasks.update(task)
            await self._uow.commit()
