"""Methods to change nuclide abundance in compositions."""

import pandas as pd

from mckit_nuclides.nuclides import NUCLIDES_TABLE


def convert_to_atomic_fraction(df: pd.DataFrame) -> pd.DataFrame:
    """Change fractions by mass to fractions by atoms.

    Args:
        df: Pandas DataFrame with having column "fraction" and
            indexed by MultipleIndex (atomic_number, mass_number)

    Returns:
        DataFrame: df with modified column "fraction"
    """
    df["fraction"] = (
        df["fraction"].values / NUCLIDES_TABLE.loc[df.index]["nuclide_mass"].values
    )
    return df
