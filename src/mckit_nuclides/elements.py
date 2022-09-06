"""Module `elements` provides access to information on chemical element level."""

from typing import Union, cast

from dataclasses import InitVar, dataclass, field

import pandas as pd

from mckit_nuclides.utils.resource import path_resolver
from multipledispatch import dispatch


def _load_elements() -> pd.DataFrame:
    path = path_resolver("mckit_nuclides")("data/elements.csv")
    converters = {
        "atomic_number": int,
        "symbol": str,
        "name": str,
        "atomic_mass": float,
        "cpk_hex_color": lambda x: int(x, base=16) if x and str.isalnum(x) else x,
        "electron_configuration": str,
        "electronegativity": lambda x: float(x) if x else x,
        "atomic_radius": lambda x: float(x) if x else x,
        "ionization_energy": lambda x: float(x) if x else x,
        "electron_affinity": lambda x: float(x) if x else x,
        "oxidation_states": str,
        "standard_state": str,
        "melting_point": lambda x: float(x) if x else x,
        "boiling_point": lambda x: float(x) if x else x,
        "density": lambda x: float(x) if x else x,
        "group_block": str,
        "year_discovered": lambda x: int(x) if str.isnumeric(x) else x,
        "period": int,
        "group": int,
    }
    return pd.read_csv(path, index_col="symbol", converters=converters)


ELEMENTS_TABLE = _load_elements()

__all__ = [
    "ELEMENTS_TABLE",
    "Element",
    "atomic_mass",
    "atomic_number",
    "symbol",
    "z",
]


def atomic_number(element: str) -> int:
    """Get atomic number (Z) for an element.

    Args:
        element: element by chemical symbol

    Returns:
        int: Z - the atomic number for the element.
    """
    return cast(int, ELEMENTS_TABLE.loc[element]["atomic_number"])


z = atomic_number


def symbol(_atomic_number: int) -> str:
    """Get chemical symbol for a given Z (atomic number).

    Args:
        _atomic_number: Z of an element

    Returns:
        str: Chemical symbol
    """
    return ELEMENTS_TABLE.index[_atomic_number - 1]  # type: ignore[no-any-return]


@dispatch(int)
def atomic_mass(_atomic_number: int) -> float:
    """Get standard atomic mass for and Element by atomic number.

    Args:
        _atomic_number: define Element by atomic number

    Returns:
        Average atomic mass of the Element with the atomic number.
    """
    return ELEMENTS_TABLE.iloc[_atomic_number - 1]["atomic_mass"]


@dispatch(str)  # type: ignore[no-redef]
def atomic_mass(_symbol: str) -> float:  # noqa: F811
    """Get standard atomic mass for and Element by symbol.

    Args:
        _symbol: define Element by symbol.

    Returns:
        Average atomic mass of the Element with the atomic number.
    """
    return ELEMENTS_TABLE.loc[_symbol]["atomic_mass"]


@dataclass
class Element:
    """Accessor to a chemical element information."""

    element: InitVar[Union[int, str]]
    atomic_number: int = field(init=False)

    def __post_init__(self, element: Union[int, str]) -> None:
        """Create an Element either from symbol or atomic number (Z).

        Args:
            element: symbol or atomic number for new Element.

        Raises:
            TypeError: if element type is not str or int.
        """
        if isinstance(element, str):
            self.atomic_number = z(element)
        elif isinstance(element, int):
            self.atomic_number = element
        else:
            raise TypeError(f"Illegal parameter symbol {element}")

    @property
    def z(self) -> int:
        """Atomic number and Z are synonymous.

        Returns:
            atomic number
        """
        return self.atomic_number

    @property
    def symbol(self) -> str:
        """Get periodical table symbol for the Element.

        Returns:
            Chemical symbol of the element.
        """
        return symbol(self.atomic_number)

    def __getattr__(self, item):
        """Use columns of ELEMENTS_TABLE as properties of the Element accessor.

        The `column` can be anything selecting a column or columns from ELEMENTS_TABLE.

        Args:
            item: column of ELEMENTS_TABLE

        Returns:
            content selected for this Element instance.
        """
        return ELEMENTS_TABLE.iloc[self.atomic_number - 1][item]
