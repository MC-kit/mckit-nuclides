import pytest

from mckit_nuclides.elements import Element, get_atomic_mass


@pytest.mark.parametrize("element, expected", [("Ag", 107.868), (1, 1.008)])
def test_get_atomic_mass(element, expected):
    assert expected == get_atomic_mass(element)


@pytest.mark.parametrize("element, expected", [("B", "Boron"), ("Og", "Oganesson")])
def test_get_name(element, expected):
    e = Element(element)
    assert expected == e.name


def test_z():
    e = Element(11)
    assert e.z == e.atomic_number


def test_element_with_invalid_key():
    with pytest.raises(TypeError):
        print(Element(3.1415926))


def test_get_unknown_property():
    with pytest.raises(KeyError):
        print(Element("Ar").unknown)


if __name__ == "__main__":
    pytest.main()
