from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC), init=False)
