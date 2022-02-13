import pandas as pd
import pytest

from mckit_nuclides.abundance import convert_to_atomic_fraction
from mckit_nuclides.elements import get_atomic_mass
from numpy.testing import assert_array_almost_equal


def test_convert_to_atomic_fraction_h2o():
    index = pd.MultiIndex.from_tuples([(1, 1), (8, 16)])
    material = pd.DataFrame(
        dict(fraction=[2 * get_atomic_mass(1), get_atomic_mass(8)]), index=index
    )
    convert_to_atomic_fraction(material)
    assert_array_almost_equal(material["fraction"].values, [2.0, 1.0], decimal=3)


if __name__ == "__main__":
    pytest.main()
