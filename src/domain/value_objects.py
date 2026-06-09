import re
from dataclasses import dataclass
from enum import StrEnum

from src.domain.exceptions import InvalidEmailError

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class EmailValueObject:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_REGEX.fullmatch(self.value):
            raise InvalidEmailError(f"Invalid email format: {self.value!r}")

    @classmethod
    def create(cls, raw: str) -> "EmailValueObject":
        return cls(value=raw.strip().lower())

    def __str__(self) -> str:
        return self.value


class TaskStatusEnum(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
