import pytest

from mckit_nuclides.nuclides import *


@pytest.mark.parametrize(
    "inp, expected, msg", [(("H", 1), ("H", 1), "At least Hydrogen should be found")]
)
def test_get_nuclide_by_element_and_isotope(inp, expected, msg):
    actual = nuclide(*inp)
    assert actual == Nuclide(*expected), msg
    actual_mass = get_atomic_mass(actual)
    assert actual_mass == 1.00782503223


@pytest.mark.parametrize(
    "inp, expected, msg",
    [
        ((1, 1), "H", "At least Hydrogen should be found"),
        ((1, 2), "H", "And deuterium should have chemical symbol H"),
    ],
)
def test_get_nuclide_by_element_and_isotope(inp, expected, msg):
    actual = nuclide(*inp).symbol
    assert actual == expected, msg
