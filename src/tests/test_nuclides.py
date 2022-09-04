import pytest

from mckit_nuclides.nuclides import Nuclide, get_nuclide_mass


@pytest.mark.parametrize(
    "inp, expected, msg", [(("H", 1), ("H", 1), "At least Hydrogen should be found")]
)
def test_get_nuclide_by_element_and_isotope(inp, expected, msg):
    actual = Nuclide(*inp)
    assert actual == Nuclide(*expected), msg
    actual_mass = actual.nuclide_mass
    assert actual.a == actual.mass_number
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
    actual = Nuclide(*inp)
    assert actual.symbol == expected
    assert actual.a == actual.mass_number


@pytest.mark.parametrize(
    "element, mass_number, expected, msg",
    [
        (1, 1, 1.0078, "At least Hydrogen should be found"),
        ("H", 2, 2.014, "Deuterium mass"),
        ("Ag", 111, 110.905, "Ag mass"),
    ],
)
def test_get_nuclide_mass(element, mass_number, expected, msg):
    actual = get_nuclide_mass(element, mass_number)
    assert actual == pytest.approx(expected, rel=1e-4), msg
