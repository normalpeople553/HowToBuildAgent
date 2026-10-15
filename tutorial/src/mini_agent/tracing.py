"""Small in-memory traces for learning and tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TraceEvent:
    kind: str
    data: dict[str, Any]


class TraceRecorder:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def add(self, kind: str, **data: Any) -> None:
        self.events.append(TraceEvent(kind=kind, data=data))
