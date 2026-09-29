from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class Link:
    slug: str
    target_url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))