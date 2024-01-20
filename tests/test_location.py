# dependencies
from azely.location import Location, get_location
from pytest import mark


# test data
locations = [
    Location(
        name="Atacama Large Millimeter/submillimeter Array",
        longitude="-67d45m11.06028s",
        latitude="-23d01m21.97704s",
        altitude="0m",
    ),
    Location(
        name="Gran Telescopio Milimétrico Alfonso Serrano",
        longitude="-97d18m53.23932s",
        latitude="18d59m08.66328s",
        altitude="0m",
    ),
    Location(
        name="Nobeyama Radio Astronomy Observatory",
        longitude="138d28m25.28621699s",
        latitude="35d56m34.76364s",
        altitude="0m",
    ),
]


# test functions
@mark.parametrize("obj", locations)
def test_get_location(obj: Location) -> None:
    assert get_location(obj.name, source=None) == obj
