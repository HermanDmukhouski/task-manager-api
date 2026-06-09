from dataclasses import dataclass

from src.domain.events.base import DomainEvent


@dataclass(frozen=True)
class UserCreatedEvent(DomainEvent):
    email: str
    name: str
