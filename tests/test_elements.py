from __future__ import annotations

import pytest

from mckit_nuclides.elements import (
    atomic_mass,
    atomic_number,
    from_molecular_formula,
    get_property,
    name,
    symbol,
    z,
)


def test_symbol() -> None:
    assert symbol(1) == "H"


@pytest.mark.parametrize("element,expected", [("Ag", 107.868), (1, 1.008)])
def test_atomic_mass(element: str, expected: float) -> None:
    assert expected == pytest.approx(atomic_mass(element))


@pytest.mark.parametrize("element,expected", [("B", "Boron"), ("Og", "Oganesson")])
def test_name(element: str, expected: str) -> None:
    assert expected == name(element)


def test_z() -> None:
    assert z("H") == atomic_number("H")


def test_element_with_invalid_key() -> None:
    with pytest.raises(KeyError):
        get_property(1000000, "name")


def test_get_unknown_property() -> None:
    with pytest.raises(KeyError):
        get_property("Ar", "unknown")


def test_from_molecular_formula() -> None:
    actual = from_molecular_formula("H2O")  # fraction by atomic
    assert actual.height == 2
    assert actual.select("fraction").sum().item() == pytest.approx(1.0)
    assert actual.filter(atomic_number=1).select("fraction").item() == pytest.approx(
        0.66666, rel=1e-4
    )


if __name__ == "__main__":
    pytest.main()
