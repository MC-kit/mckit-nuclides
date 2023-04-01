from __future__ import annotations

import pytest

from mckit_nuclides.elements import atomic_mass
from mckit_nuclides.nuclides import NUCLIDES_TABLE, get_nuclide_mass


@pytest.mark.parametrize(
    "inp,expected,msg", [(("H", 1), 1.00782503223, "At least Hydrogen should be found")]
)
def test_get_nuclide_by_element_and_isotope(inp, expected, msg):
    actual = get_nuclide_mass(*inp)
    assert actual == expected
    assert actual != atomic_mass(inp[0]), "Average Element mass differs from an Nuclide mass."


@pytest.mark.parametrize(
    "inp,expected,msg",
    [
        ((1, 1), "H", "At least Hydrogen should be found"),
        ((1, 2), "H", "And deuterium should have chemical symbol H"),
    ],
)
def test_get_nuclide_by_z_and_isotope(inp, expected, msg):
    actual = NUCLIDES_TABLE.loc[inp]
    assert actual["symbol"] == expected
    assert actual.name == inp


@pytest.mark.parametrize(
    "element,mass_number,expected,msg",
    [
        (1, 1, 1.0078, "At least Hydrogen should be found"),
        ("H", 2, 2.014, "Deuterium mass"),
        ("Ag", 111, 110.905, "Ag mass"),
    ],
)
def test_get_nuclide_mass(element, mass_number, expected, msg):
    actual = get_nuclide_mass(element, mass_number)
    assert actual == pytest.approx(expected, rel=1e-4), msg
