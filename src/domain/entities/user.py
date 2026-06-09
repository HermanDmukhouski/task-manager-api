from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime

from src.domain.entities.base import AggregateRoot
from src.domain.events.user_events import UserCreatedEvent
from src.domain.exceptions import EmptyNameError
from src.domain.value_objects import EmailValueObject


@dataclass
class UserAggregate(AggregateRoot):
    email: EmailValueObject
    name: str
    created_at: datetime
    id: int | None = field(default=None)

    @classmethod
    def create(cls, email: str, name: str) -> "UserAggregate":
        stripped_name = name.strip()
        if not stripped_name:
            raise EmptyNameError("Name cannot be empty")
        email_vo = EmailValueObject.create(email)
        user = cls(
            email=email_vo,
            name=stripped_name,
            created_at=datetime.now(UTC),
        )
        user._record_event(UserCreatedEvent(email=email_vo.value, name=stripped_name))
        return user

    def change_name(self, name: str) -> None:
        stripped = name.strip()
        if not stripped:
            raise EmptyNameError("Name cannot be empty")
        self.name = stripped
