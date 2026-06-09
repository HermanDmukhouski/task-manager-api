from dataclasses import dataclass

from src.application.common.interfaces import Command


@dataclass(frozen=True)
class CreateUserCommand(Command):
    email: str
    name: str


@dataclass(frozen=True)
class CreateUserResult:
    user_id: int
