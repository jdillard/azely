__all__ = ["get_time"]


# standard library
from datetime import datetime, timedelta, tzinfo


# dependent packages
import pytz
from dateutil.parser import ParserError, parse
from pandas import DatetimeIndex, date_range
from pytz import UnknownTimeZoneError
from . import AzelyError, HERE, NOW, TODAY, config
from .location import get_location
from .utils import set_defaults


# main functions
@set_defaults(**config["time"])
def get_time(
    query: str = NOW,
    view: str = HERE,
    freq: str = "10T",
    sep: str = "to",
    timeout: int = 5,
) -> DatetimeIndex:
    tzinfo = parse_tzinfo(view, timeout)
    name = tzinfo.zone

    if query == NOW:
        start = end = datetime.now(tzinfo)
    elif query == TODAY:
        start = datetime.now(tzinfo).date()
        end = start + timedelta(days=1)
    elif sep in query:
        queries = query.split(sep)
        start, end = map(parse_datetime, queries)
    else:
        start = parse_datetime(query)
        end = start + timedelta(days=1)

    return date_range(start, end, None, freq, tzinfo, name=name)


# helper functions
def parse_tzinfo(query: str, timeout: int) -> tzinfo:
    try:
        return pytz.timezone(query)
    except UnknownTimeZoneError:
        return get_location(query, timeout).tzinfo


def parse_datetime(query: str) -> datetime:
    try:
        return parse(query)
    except ParserError:
        raise AzelyError(f"Failed to parse: {query}")
