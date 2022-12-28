import pytest

from mckit_nuclides.elements import (
    atomic_mass,
    atomic_number,
    get_property,
    name,
    symbol,
    z,
)


def test_symbol():
    assert symbol(1) == "H"


@pytest.mark.parametrize("element, expected", [("Ag", 107.868), (1, 1.008)])
def test_atomic_mass(element, expected):
    assert expected == atomic_mass(element)


@pytest.mark.parametrize("element, expected", [("B", "Boron"), ("Og", "Oganesson")])
def test_name(element, expected):
    assert expected == name(element)


def test_z():
    assert z("H") == atomic_number("H")


def test_element_with_invalid_key():
    with pytest.raises(IndexError):
        get_property(1000000, "name")


def test_get_unknown_property():
    with pytest.raises(KeyError):
        get_property("Ar", "unknown")


if __name__ == "__main__":
    pytest.main()
