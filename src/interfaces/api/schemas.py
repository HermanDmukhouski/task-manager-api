from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field

from src.domain.value_objects import TaskStatusEnum


class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    created_at: datetime


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4096)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    next_cursor: str | None = None


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatusEnum


class TaskStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    new: int
    in_progress: int
    done: int
    cancelled: int


class ErrorResponse(BaseModel):
    detail: str
