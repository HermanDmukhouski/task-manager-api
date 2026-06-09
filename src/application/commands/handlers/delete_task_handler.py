from src.application.commands.delete_task import DeleteTaskCommand
from src.application.common.exceptions import NotFoundError
from src.application.common.interfaces import CommandHandler
from src.application.interfaces.unit_of_work import IUnitOfWork


class DeleteTaskHandler(CommandHandler[DeleteTaskCommand, None]):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: DeleteTaskCommand) -> None:
        async with self._uow:
            task = await self._uow.tasks.get_by_id(command.task_id)
            if task is None:
                raise NotFoundError(f"Task {command.task_id} not found")

            await self._uow.tasks.delete(command.task_id)
            await self._uow.commit()
