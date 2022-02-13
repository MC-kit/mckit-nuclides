import pytest

from mckit_nuclides.nuclides import Nuclide


@pytest.mark.parametrize(
    "inp, expected, msg", [(("H", 1), ("H", 1), "At least Hydrogen should be found")]
)
def test_get_nuclide_by_element_and_isotope(inp, expected, msg):
    actual = Nuclide(*inp)
    assert actual == Nuclide(*expected), msg
    actual_mass = actual.relative_atomic_mass
    assert actual_mass == 1.00782503223
    assert (
        actual_mass != actual.atomic_mass
    ), "Average Element mass differs from an Nuclide mass."


@pytest.mark.parametrize(
    "inp, expected, msg",
    [
        ((1, 1), "H", "At least Hydrogen should be found"),
        ((1, 2), "H", "And deuterium should have chemical symbol H"),
    ],
)
def test_get_nuclide_by_z_and_isotope(inp, expected, msg):
    actual = Nuclide(*inp).symbol
    assert actual == expected, msg
