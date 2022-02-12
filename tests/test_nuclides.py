import pytest

from mckit_nuclides.nuclides import *


@pytest.mark.parametrize("inp, expected, msg", [
    (('H', 1), ('H', 1), "At least Hydrogen should be found")
])
def test_get_nuclide_by_element_and_isotope(inp, expected, msg):
    actual = nuclide(*inp)
    assert actual == Nuclide(*expected), msg
    actual_mass = get_atomic_mass(actual)
    assert actual_mass == 1.00782503223
