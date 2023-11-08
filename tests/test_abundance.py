from __future__ import annotations

from numpy.testing import assert_array_almost_equal

import pandas as pd
import pytest

from mckit_nuclides.abundance import convert_to_atomic_fraction, expand_natural_presence
from mckit_nuclides.elements import atomic_mass


@pytest.fixture()
def water():
    return pd.DataFrame(
        {"fraction": [2 * atomic_mass(1), atomic_mass(8)]},
        index=pd.MultiIndex.from_tuples([(1, 1), (8, 16)]),
    )


def test_convert_to_atomic_fraction_h2o(water):
    convert_to_atomic_fraction(water)
    assert_array_almost_equal(water["fraction"].to_numpy(), [2.0, 1.0], decimal=3)


def test_expand_natural_presence():
    composition = [
        (1, 0, 2.0),
        (8, 16, 1.0),
    ]
    expected = [
        (1, 1, 2.0 * 0.999885),  # H, expanded from (1,0)
        (1, 2, 2.0 * 0.000115),  # D, -/-
        (8, 16, 1.0),  # O (mass_number is specified)
    ]
    actual = list(expand_natural_presence(composition))
    assert expected == actual


if __name__ == "__main__":
    pytest.main()
