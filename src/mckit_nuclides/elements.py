"""Module `elements` provides access to information on chemical element level."""
from __future__ import annotations

from typing import cast

from pathlib import Path

import polars as pl

HERE = Path(__file__).parent

ELEMENTS_TABLE_PL = pl.read_parquet(HERE / "data/elements.parquet")


def atomic_number(element: str) -> int:
    """Get atomic number (Z) for an element.

    Args:
        element: element by chemical symbol

    Returns:
        int: Z - the atomic number for the element.
    """
    return cast(
        int, ELEMENTS_TABLE_PL.filter(pl.col("symbol").eq(element)).select("atomic_number").item(),
    )


z = atomic_number
"""Synonym to atomic_number."""


def symbol(_atomic_number: int) -> str:
    """Get chemical symbol for a given Z (atomic number).

    Args:
        _atomic_number: Z of an element

    Returns:
        str: Chemical symbol
    """
    return ELEMENTS_TABLE_PL.filter(pl.col("atomic_number").eq(_atomic_number)).select("symbol").item()  # type: ignore[no-any-return]


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
