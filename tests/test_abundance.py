from __future__ import annotations

from numpy.testing import assert_array_almost_equal

import polars as pl
import pytest

from mckit_nuclides.abundance import (
    convert_to_atomic_fraction,
    expand_df_natural_presence,
    expand_natural_presence,
)
from mckit_nuclides.elements import from_molecular_formula


@pytest.fixture()
def water() -> pl.DataFrame:
    return (
        from_molecular_formula("H2O", mass_fraction=True)
        .with_columns(mass_number=pl.lit(0))
        .select("atomic_number", "mass_number", "fraction")
    )


def test_convert_to_atomic_fraction_h2o(water) -> None:
    new_water = convert_to_atomic_fraction(water)
    assert_array_almost_equal(new_water["fraction"].to_numpy(), [2.0 / 3, 1.0 / 3], decimal=3)


def test_expand_natural_presence() -> None:
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
    assert_array_almost_equal(expected, actual)


def test_expand_df_natural_presence(water):
    new_water = convert_to_atomic_fraction(water)
    expanded = expand_df_natural_presence(new_water)
    expected = pl.DataFrame(
        {
            "atomic_number": pl.Series([1, 1, 8, 8, 8], dtype=pl.UInt8),
            "mass_number": pl.Series([1, 2, 16, 17, 18], dtype=pl.UInt16),
            "fraction": [0.66659, 0.000077, 0.332523, 0.000127, 0.000683],
        },
    )
    assert (
        expanded.select("atomic_number", "mass_number")
        == expected.select("atomic_number", "mass_number")
    ).filter(pl.col("atomic_number").not_() | pl.col("mass_number").not_()).height == 0
    assert (
        expanded.join(expected, on=["atomic_number", "mass_number"])
        .select(
            (pl.col("fraction") - pl.col("fraction_right")).abs().alias("diff"),
            (pl.col("fraction") + pl.col("fraction_right")).alias("sum"),
        )
        .select(eval=pl.col("diff") / pl.col("sum") < 1e-2)
        .filter(pl.col("eval").not_())
        .height
        == 0
    )


if __name__ == "__main__":
    pytest.main()
