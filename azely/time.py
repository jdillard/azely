__all__ = ["Time"]


# standard library
from dataclasses import dataclass
from typing import Optional


@dataclass
class Time:
    """Time information."""

    name: str
    """Name of the time."""

    start: str
    """Left bound of the time (inclusive, timezone-naive)."""

    end: str
    """Right bound of the time (exclusive, timezone-naive)."""

    view: Optional[str]
    """Timezone name of location name for the timezone."""
