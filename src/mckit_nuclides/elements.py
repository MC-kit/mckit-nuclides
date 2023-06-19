"""Module `elements` provides access to information on chemical element level."""
from __future__ import annotations

from typing import Union, cast

import pandas as pd

from mckit_nuclides.utils.resource import path_resolver

TableValue = Union[int, str, float, None]


def _opt_float(x: str | None) -> float | None:
    return float(x) if x else None


def _load_elements() -> pd.DataFrame:
    converters = {
        "atomic_number": int,
        "symbol": str,
        "name": str,
        "atomic_mass": float,
        "cpk_hex_color": lambda x: int(x, base=16) if x and str.isalnum(x) else x,
        "electron_configuration": str,
        "electronegativity": _opt_float,
        "atomic_radius": _opt_float,
        "ionization_energy": _opt_float,
        "electron_affinity": _opt_float,
        "oxidation_states": str,
        "standard_state": str,
        "melting_point": _opt_float,
        "boiling_point": _opt_float,
        "density": _opt_float,
        "group_block": str,
        "year_discovered": lambda x: int(x) if str.isnumeric(x) else x,
        "period": int,
        "group": int,
    }
    path = path_resolver("mckit_nuclides")("data/elements.csv")
    with path.open(encoding="utf-8") as fid:
        return pd.read_csv(fid, index_col="symbol", converters=converters)


ELEMENTS_TABLE = _load_elements()


def atomic_number(element: str) -> int:
    """Get atomic number (Z) for an element.

    Args:
        element: element by chemical symbol

    Returns:
        int: Z - the atomic number for the element.
    """
    return cast(int, ELEMENTS_TABLE.loc[element, "atomic_number"])


z = atomic_number
"""Synonym to atomic_number."""


def symbol(_atomic_number: int) -> str:
    """Get chemical symbol for a given Z (atomic number).

    Args:
        _atomic_number: Z of an element

    Returns:
        str: Chemical symbol
    """
    return ELEMENTS_TABLE.index[_atomic_number - 1]  # type: ignore[no-any-return]


def get_property(z_or_symbol: int | str, column: str) -> TableValue:
    """Get column value for an element specified with atomic number or symbol.

    Args:
        z_or_symbol: define either by atomic number or symbol
        column: column name in ELEMENTS_TABLE

    Returns:
        The column value for the given element.
    """
    if isinstance(z_or_symbol, int):
        return cast(
            TableValue,
            ELEMENTS_TABLE.iloc[z_or_symbol - 1, ELEMENTS_TABLE.columns.get_loc(column)],
        )
    return cast(TableValue, ELEMENTS_TABLE.loc[z_or_symbol, [column]].item())


def atomic_mass(z_or_symbol: int | str) -> float:
    """Get standard atomic mass for and Element by atomic number.

    Args:
        z_or_symbol: define either by atomic number or symbol

    Returns:
        Average atomic mass of the Element with the atomic number.
    """
    return cast(float, get_property(z_or_symbol, "atomic_mass"))


def name(z_or_symbol: int | str) -> str:
    """Get standard atomic mass for and Element by atomic number.

    Args:
        z_or_symbol: define either by atomic number or symbol

    Returns:
        The name of the element.
    """
    return cast(str, get_property(z_or_symbol, "name"))


__all__ = [n for n in locals() if not n.startswith("_")]
