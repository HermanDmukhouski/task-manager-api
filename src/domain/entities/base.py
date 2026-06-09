from dataclasses import dataclass
from dataclasses import field

from src.domain.events.base import DomainEvent


@dataclass
class AggregateRoot:
    _domain_events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
        compare=False,
    )

    def pull_domain_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)
