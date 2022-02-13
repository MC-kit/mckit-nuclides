"""Methods to change nuclide abundance in compositions."""

import pandas as pd

from mckit_nuclides.nuclides import NUCLIDES_TABLE


def convert_to_atomic_fraction(df: pd.DataFrame) -> pd.DataFrame:
    """Change fractions by mass to fractions by atoms.

    Args:
        df: Pandas DataFrame with having column "fractions" and
            indexed by MultipleIndex (atomic_number, mass_number)

    Returns:
        DataFrame: df with modified column "fractions"
    """
    df["fraction"] /= NUCLIDES_TABLE.loc[df.index]["relative_atomic_mass"]
    return df
