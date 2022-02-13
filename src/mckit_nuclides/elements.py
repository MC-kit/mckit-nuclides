"""Module `elements` provides access to information on chemical element level."""

from typing import Union, cast

from dataclasses import InitVar, dataclass, field

import pandas as pd

from mckit_nuclides.utils.resource import path_resolver
from multipledispatch import dispatch


def _load_elements() -> pd.DataFrame:
    path = path_resolver("mckit_nuclides")("data/elements.csv")
    return pd.read_csv(path, index_col="Symbol")


ELEMENTS_TABLE = _load_elements()


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
            self.atomic_number = ELEMENTS_TABLE.loc[element]["AtomicNumber"]
        elif isinstance(element, int):
            self.atomic_number = element
        else:  # pragma nocover
            raise TypeError(f"Illegal parameter symbol {element}")

    @property
    def z(self) -> int:
        """Atomic number and Z are synonymous.

        Returns:
            atomic number
        """
        return self.atomic_number

    @property
    def name(self) -> str:
        """Get the name of the Element.

        Returns:
            English name for the Element.
        """
        return cast(str, ELEMENTS_TABLE.iloc[self.atomic_number - 1]["Name"])

    @property
    def symbol(self) -> str:
        """Get periodical table symbol for the Element.

        Returns:
            Chemical symbol of the element.
        """
        return ELEMENTS_TABLE.index[self.atomic_number - 1]  # type: ignore[no-any-return]

    @property
    def atomic_mass(self) -> float:
        """Get atomic mass.

        Returns:
            atomic mass in a.u.
        """
        return cast(float, ELEMENTS_TABLE.iloc[self.atomic_number - 1]["AtomicMass"])

    # @classmethod
    # def from_dict(cls, data: Dict) -> "Element":
    #     """Helper for JSON information retrieval."""
    #     return cls(data["atomic_number"])


@dispatch(int)
def get_atomic_mass(atomic_number: int) -> float:
    """Get standard atomic mass for and Element by atomic number.

    Args:
        atomic_number: define Element by atomic number

    Returns:
        Average atomic mass of the Element with the atomic number.
    """
    return ELEMENTS_TABLE.iloc[atomic_number - 1]["AtomicMass"]


@dispatch(str)  # type: ignore[no-redef]
def get_atomic_mass(symbol: str) -> float:  # noqa: F811
    """Get standard atomic mass for and Element by symbol.

    Args:
        symbol: define Element by symbol.

    Returns:
        Average atomic mass of the Element with the atomic number.
    """
    return ELEMENTS_TABLE.loc[symbol]["AtomicMass"]
