from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.domain.entities.task import TaskAggregate
from src.domain.entities.user import UserAggregate
from src.domain.value_objects import EmailValueObject
from src.domain.value_objects import TaskStatusEnum


class Base(DeclarativeBase):
    pass


class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[int | None] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TaskTable(Base):
    __tablename__ = "tasks"

    id: Mapped[int | None] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def user_to_domain(row: UserTable) -> UserAggregate:
    if row.id is None:
        raise ValueError("Cannot map unpersisted user row to domain")
    return UserAggregate(
        id=row.id,
        email=EmailValueObject(value=row.email),
        name=row.name,
        created_at=row.created_at,
    )


def user_from_domain(user: UserAggregate) -> UserTable:
    return UserTable(
        email=user.email.value,
        name=user.name,
        created_at=user.created_at,
    )


def task_to_domain(row: TaskTable) -> TaskAggregate:
    if row.id is None:
        raise ValueError("Cannot map unpersisted task row to domain")
    return TaskAggregate(
        id=row.id,
        user_id=row.user_id,
        title=row.title,
        description=row.description,
        status=TaskStatusEnum(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def task_from_domain(task: TaskAggregate) -> TaskTable:
    return TaskTable(
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
