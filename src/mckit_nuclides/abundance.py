"""Methods to convert fractions from mass to atoms adn from averaged by mass number to natural."""

import pandas as pd

from mckit_nuclides.nuclides import NUCLIDES_TABLE


def convert_to_atomic_fraction(df: pd.DataFrame) -> None:
    df["fraction"] /= NUCLIDES_TABLE.loc[df.index]["relative_atomic_mass"]
