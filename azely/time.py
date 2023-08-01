__all__ = ["Time", "get_time"]


# standard library
from dataclasses import dataclass
from functools import partial
from re import compile
from typing import Optional


# dependencies
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .consts import AZELY_CACHE
from .location import get_location
from .utils import PathLike, cache, rename


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

    timezone: Optional[str] = None
    """IANA timezone name of the time."""


@partial(rename, key="name")
@partial(cache, table="times")
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

    if (view := view_end or view_start) is None:
        return Time(
            name=query,
            start=time_start,
            end=time_end,
        )
    else:
        return Time(
            name=query,
            start=time_start,
            end=time_end,
            timezone=parse_timezone(view),
        )


def parse_timezone(query: str) -> str:
    """Return an IANA timezone name from a query."""
    try:
        return str(ZoneInfo(query))
    except ZoneInfoNotFoundError:
        loc = get_location(query, update=True)
        return str(loc.timezone)


def split_bound(query: str) -> tuple[str, Optional[str]]:
    """Split a bound into time and view."""
    for sep in BOUND_SEPS:
        if len(split := sep.split(query, 1)) == 2:
            return split[0].strip(), split[1].strip()

    return query.strip(), DEFAULT_VIEW


def split_query(query: str) -> tuple[str, str]:
    """Split a query into start and end bounds."""
    for sep in QUERY_SEPS:
        if len(split := sep.split(query, 1)) == 2:
            return split[0].strip(), split[1].strip()

    return query.strip(), DEFAULT_END
