from sqlalchemy import case
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.pagination import TaskCursor
from src.application.interfaces.repositories import ITaskRepository
from src.application.interfaces.repositories import TaskStats
from src.domain.entities.task import TaskAggregate
from src.domain.value_objects import TaskStatusEnum
from src.infrastructure.db.models import TaskTable
from src.infrastructure.db.models import task_from_domain
from src.infrastructure.db.models import task_to_domain


class TaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, task: TaskAggregate) -> None:
        row = task_from_domain(task)
        self._session.add(row)
        await self._session.flush()
        task.id = row.id

    async def get_by_id(self, task_id: int) -> TaskAggregate | None:
        row = await self._session.get(TaskTable, task_id)
        if row is None:
            return None
        return task_to_domain(row)

    async def get_by_user_id(
        self,
        user_id: int,
        status: TaskStatusEnum | None,
        limit: int,
        cursor: TaskCursor | None,
    ) -> list[TaskAggregate]:
        stmt = select(TaskTable).where(TaskTable.user_id == user_id)
        if status is not None:
            stmt = stmt.where(TaskTable.status == status.value)
        if cursor is not None:
            stmt = stmt.where(
                tuple_(TaskTable.created_at, TaskTable.id) < (cursor.created_at, cursor.id)
            )
        stmt = stmt.order_by(TaskTable.created_at.desc(), TaskTable.id.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return [task_to_domain(row) for row in result.scalars()]

    async def update(self, task: TaskAggregate) -> None:
        row = await self._session.get(TaskTable, task.id)
        if row is not None:
            row.title = task.title
            row.description = task.description
            row.status = task.status.value
            row.updated_at = task.updated_at
            await self._session.flush()

    async def delete(self, task_id: int) -> None:
        await self._session.execute(delete(TaskTable).where(TaskTable.id == task_id))

    async def get_stats_by_user(self, user_id: int) -> TaskStats:
        stmt = select(
            func.count().label("total"),
            func.count(case((TaskTable.status == TaskStatusEnum.NEW, 1))).label("new"),
            func.count(case((TaskTable.status == TaskStatusEnum.IN_PROGRESS, 1))).label(
                "in_progress"
            ),
            func.count(case((TaskTable.status == TaskStatusEnum.DONE, 1))).label("done"),
            func.count(case((TaskTable.status == TaskStatusEnum.CANCELLED, 1))).label("cancelled"),
        ).where(TaskTable.user_id == user_id)
        result = await self._session.execute(stmt)
        row = result.one()
        return TaskStats(
            total=row.total,
            new=row.new,
            in_progress=row.in_progress,
            done=row.done,
            cancelled=row.cancelled,
        )
