__all__ = ["Time", "get_time"]


# standard library
from dataclasses import dataclass
from re import compile
from typing import Optional


# dependencies
from .consts import AZELY_CACHE
from .utils import PathLike


# constants
BOUND_SEPS = (
    compile(r"(?<!^)@"),
    compile(r"(?<!^)in"),
)
DEFAULT_END = "In 1 day"
DEFAULT_VIEW = None
QUERY_SEPS = (
    compile(r"(?<!^)→"),
    compile(r"(?<!^)->"),
    compile(r"(?<!^)to"),
)


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


def get_time(
    query: str,
    /,
    *,
    # consumed by decorators
    name: Optional[str] = None,  # @cache
    source: PathLike = AZELY_CACHE,  # @cache
    update: bool = False,  # @cache
) -> Time:
    """Get time information."""
    start, end = split_query(query)
    time_start, view_start = split_bound(start)
    time_end, view_end = split_bound(end)

    return Time(
        name=query,
        start=time_start,
        end=time_end,
        view=view_end or view_start or None,
    )


def split_bound(bound: str) -> tuple[str, Optional[str]]:
    """Split a bound into time and view."""
    for sep in BOUND_SEPS:
        if len(split := sep.split(bound, 1)) == 2:
            return split[0].strip(), split[1].strip()

    return bound.strip(), DEFAULT_VIEW


def split_query(query: str) -> tuple[str, str]:
    """Split a query into start and end bounds."""
    for sep in QUERY_SEPS:
        if len(split := sep.split(query, 1)) == 2:
            return split[0].strip(), split[1].strip()

    return query.strip(), DEFAULT_END
