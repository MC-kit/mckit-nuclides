"""Information on nuclides: masses, natural presence and more."""
from __future__ import annotations

from typing import cast


from mckit_nuclides.elements import TableValue, z

NUCLIDES_TABLE = _load_tables()


def get_property(z_or_symbol: int | str, mass_number: int, column: str) -> TableValue:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        z_or_symbol: Z or symbol of a nuclide
        mass_number: A
        column: name of column to extract value from

    Returns:
        Value of a column for a given nuclide.
    """
    if isinstance(z_or_symbol, str):
        z_or_symbol = z(z_or_symbol)
    return cast(TableValue, NUCLIDES_TABLE.loc[(z_or_symbol, mass_number), column])


def get_nuclide_mass(z_or_symbol: int | str, mass_number: int) -> float:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        z_or_symbol: Z or symbol of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide (a.u).
    """
    return cast(float, get_property(z_or_symbol, mass_number, "nuclide_mass"))
