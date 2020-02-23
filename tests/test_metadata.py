# dependent packages
import azely


# test functions
def test_version():
    """Make sure the version is valid."""
    assert azely.__version__ == "0.5.1"


def test_author():
    """Make sure the author is valid."""
    assert azely.__author__ == "Akio Taniguchi"
