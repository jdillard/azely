"""Azely's object module (mid-level API).

This module mainly provides ``Object`` class for information of an astronomical
object (object information, hereafter) and ``get_object`` function to search for
object information as an instance of ``Object`` class.

The ``Object`` class is defined as
``Object(name: str, frame: str, longitude: str, latitude: str)``,
where frame is a name of equatorial coordinates (e.g., icrs) and lon/lat are values
of coordinates which must be written with units like 02h42m40.771s/-00d00m47.84s.


The ``get_object`` function acquires object information from:
(1) Data from CDS (by default). Internet connection is required.
(2) User-defined object information written in a TOML file.

In the case of (1), obtained object information is cached in a special
TOML file (``~/.config/azely/objects.toml``) for an offline use.

In the case of (2), users can define object information in a TOML file
(e.g., ``user.toml``) which should be put in a current directory or in the
Azely's config directory (``~/.config/azely``). Object information must be
defined as a table in the TOML file like::

    # user.toml

    [GC]
    name = "Galactic center"
    frame = "galactic"
    longitude = "0deg"
    latitude = "0deg"

Then object information can be obtained by ``get_object(<query>)``.
Use ``get_object(<name>:<query>)`` for user-defined object information,
where ``<name>`` must be the name of a TOML file without suffix or the full
path of it. If it does not exist in a current directory, the function
will try to find it in the Azely's config directory (``~/.config/azely``).

Examples:
    To get object info from CDS::

        >>> obj = azely.object.get_object('NGC1068')

    To get object info from ``user.toml``::

        >>> obj = azely.object.get_object('user:GC')

"""
__all__ = ["Object", "get_object"]


# standard library
from dataclasses import dataclass
from typing import List


# dependent packages
from astropy.coordinates import (
    Longitude,
    Latitude,
    SkyCoord,
    get_body,
    solar_system_ephemeris,
)
from astropy.time import Time as ObsTime
from astropy.utils.data import conf
from .cache import PathLike, cache
from .consts import AZELY_OBJECT, FRAME, TIMEOUT
from .query import parse


SOLAR_BODIES: List[str] = list(solar_system_ephemeris.bodies)  # type: ignore
SOLAR_FRAME = "solar"


@dataclass
class Object:
    """Object information."""

    name: str
    """Name of the object."""

    longitude: str
    """Longitude (e.g. R.A. or l) of the object."""

    latitude: str
    """Latitude (e.g. Dec. or b) of the object."""

    frame: str
    """Equatorial coordinates of the object."""

    def __post_init__(self) -> None:
        """Add or update units of object coordinates."""
        if not self.is_solar:
            self.longitude = str(Longitude(self.longitude, "hr"))
            self.latitude = str(Latitude(self.latitude, "deg"))

    @property
    def is_solar(self) -> bool:
        """Whether it is a solar object."""
        return self.frame == SOLAR_FRAME

    def to_skycoord(self, obstime: ObsTime) -> SkyCoord:
        """Convert it to a SkyCoord object."""
        if self.is_solar:
            skycoord = get_body(
                body=self.name,
                time=obstime,
            )
        else:
            skycoord = SkyCoord(
                self.longitude,
                self.latitude,
                frame=self.frame,
                obstime=obstime,
            )

        skycoord.location = obstime.location
        skycoord.info.name = self.name  # type: ignore
        return skycoord


# main functions
def get_object(query: str, frame: str = FRAME, timeout: int = TIMEOUT) -> Object:
    """Get object information by various ways.

    This function acquires object information by the following two ways:
    (1) Data from CDS (by default). Internet connection is required.
    (2) User-defined object information written in a TOML file.

    In the case of (1), obtained object information is cached in a special
    TOML file (``~/.config/azely/objects.toml``) for an offline use.

    In the case of (2), users can define object information in a TOML file
    (e.g., ``user.toml``) which should be put in a current directory or in the
    Azely's config directory (``~/.config/azely``).

    Then object information can be obtained by ``get_object(<query>)``.
    Use ``get_object(<name>:<query>)`` for user-defined object information,
    where ``<name>`` must be the name of a TOML file without suffix or the full
    path of it. If it does not exist in a current directory, the function
    will try to find it in the Azely's config directory (``~/.config/azely``).

    Args:
        query: Query string (e.g., ``'NGC1068'`` or ``'user:GC'``).
        frame: Name of equatorial coordinates used in astropy's SkyCoord.
        timeout: Query timeout expressed in units of seconds.

    Returns:
        Object information as an instance of ``Object`` class.

    Raises:
        AzelyError: Raised if the function fails to get object information.

    Notes:
        As ``object`` is the Python's builtin base class, it might be better
        to use an alternative variable name (e.g., ``object_`` or ``obj``)
        for object information which this function returns.

    Examples:
        To get object info from CDS::

            >>> obj = azely.object.get_object('NGC1068')

        To get object info from ``user.toml``::

            >>> obj = azely.object.get_object('user:GC')

    """
    parsed = parse(query)

    if parsed.query.lower() in SOLAR_BODIES:
        return get_object_solar(
            query=parsed.query,
            source=parsed.source or AZELY_OBJECT,
            update=parsed.update,
        )
    else:
        return get_object_by_name(
            query=parsed.query,
            frame=frame,
            timeout=timeout,
            source=parsed.source or AZELY_OBJECT,
            update=parsed.update,
        )


@cache
def get_object_solar(
    query: str,
    source: PathLike,  # consumed by @cache
    update: bool,  # consumed by @cache
) -> Object:
    """Get object information of the solar system."""
    return Object(query.capitalize(), SOLAR_FRAME, "", "")


@cache
def get_object_by_name(
    query: str,
    frame: str,
    timeout: int,
    source: PathLike,  # consumed by @cache
    update: bool,  # consumed by @cache
) -> Object:
    """Get object information from CDS."""
    with Conf.remote_timeout.set_temp(timeout):  # type: ignore
        try:
            res = SkyCoord.from_name(query, frame)
            lon, lat = res.to_string("hmsdms").split()  # type: ignore
        except NameResolveError:
            raise AzelyError(f"Failed to get object: {query}")
        except ValueError:
            raise AzelyError(f"Failed to parse frame: {frame}")

    return Object(query, frame, lon, lat)
