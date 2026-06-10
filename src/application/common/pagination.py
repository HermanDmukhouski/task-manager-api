import base64
import binascii
from datetime import datetime
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationError

from src.application.common.exceptions import InvalidCursorError


class TaskCursor(BaseModel):
    model_config = ConfigDict(frozen=True)

    created_at: datetime
    id: int

    def encode(self) -> str:
        raw = self.model_dump_json().encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @classmethod
    def decode(cls, token: str) -> Self:
        padded = token + "=" * (-len(token) % 4)
        try:
            raw = base64.urlsafe_b64decode(padded.encode())
            return cls.model_validate_json(raw)
        except (binascii.Error, UnicodeDecodeError, ValidationError) as exc:
            raise InvalidCursorError("Invalid pagination cursor") from exc
