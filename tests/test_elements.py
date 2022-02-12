import pytest

from mckit_nuclides.elements import Element, get_atomic_mass


@pytest.mark.parametrize("element, expected", [("Ag", 107.868), (1, 1.008)])
def test_get_atomic_mass(element, expected):
    assert expected == get_atomic_mass(element)


@pytest.mark.parametrize("element, expected", [("B", "Boron"), ("Og", "Oganesson")])
def test_get_name(element, expected):
    assert expected == Element(element).name


if __name__ == "__main__":
    pytest.main()
