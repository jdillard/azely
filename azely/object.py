__all__ = ["get_object"]


# standard library
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Tuple


# dependent packages
from astropy.coordinates import SkyCoord, solar_system_ephemeris
from astropy.coordinates.name_resolve import NameResolveError
from astropy.utils.data import Conf
from .utils import AzelyError, TOMLDict, cache_to


# constants
from .consts import (
    AZELY_DIR,
    AZELY_OBJECT,
    FRAME,
    TIMEOUT,
)

DELIMITER = ":"
SOLAR = "solar"
TOML_SUFFIX = ".toml"


# data classes
@dataclass(frozen=True)
class Object:
    name: str
    frame: str
    longitude: str
    latitude: str

    @property
    def is_solar(self) -> bool:
        return self.frame == SOLAR

    @property
    def coords(self) -> Tuple[str]:
        return self.longitude, self.latitude


# main functions
def get_object(query: str, frame: str = FRAME, timeout: int = TIMEOUT) -> Object:
    if DELIMITER in query:
        return Object(**get_object_by_user(query))
    elif query.lower() in solar_system_ephemeris.bodies:
        return Object(**get_object_of_solar(query))
    else:
        return Object(**get_object_by_query(query, frame, timeout))


# helper functions
def get_object_by_user(query: str) -> Dict[str, str]:
    path, query = query.split(DELIMITER)
    path = Path(path).with_suffix(TOML_SUFFIX).expanduser()

    if not path.exists():
        path = AZELY_DIR / path

    if not path.exists():
        raise AzelyError(f"Failed to find path: {path}")

    try:
        return TOMLDict(path)[query]
    except KeyError:
        raise AzelyError(f"Failed to get object: {query}")


@cache_to(AZELY_OBJECT)
def get_object_of_solar(query: str) -> Dict[str, str]:
    return asdict(Object(query, SOLAR, "NaN", "NaN"))


@cache_to(AZELY_OBJECT)
def get_object_by_query(query: str, frame: str, timeout: int) -> Dict[str, str]:
    with Conf.remote_timeout.set_temp(timeout):
        try:
            res = SkyCoord.from_name(query, frame)
        except NameResolveError:
            raise AzelyError(f"Failed to get object: {query}")
        except ValueError:
            raise AzelyError(f"Failed to parse frame: {frame}")

    return asdict(Object(query, frame, *res.to_string("hmsdms").split()))
