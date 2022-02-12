"""Information on nuclides: masses, natural presence and more."""

from typing import Any, Dict, List, Tuple, Union, cast

from dataclasses import dataclass
from functools import reduce

import pandas as pd

from mckit_nuclides.elements import Element
from mckit_nuclides.utils.resource import path_resolver
from multipledispatch import dispatch


def _load_tables() -> Tuple[Dict[str, int], Dict[int, str], pd.DataFrame]:
    path = path_resolver("mckit_nuclides")(
        "data/nist_atomic_weights_and_element_compositions.txt"
    )

    collector: Dict[str, List[Any]] = dict(
        atomic_number=[],
        atomic_symbol=[],
        mass_number=[],
        relative_atomic_mass=[],
        isotopic_composition=[],
    )

    types = dict(
        atomic_number=int,
        mass_number=int,
        relative_atomic_mass=float,
        isotopic_composition=float,
    )

    # noinspection PyTypeChecker
    def _split_line(line: str) -> Tuple[str, Any]:
        label, value = map(str.strip, line.split("="))  # type: str, str
        label = label.lower().replace(" ", "_")
        value_type = types.get(label, None)
        if value_type is not None:
            if value:
                value = value.split("(", 1)[
                    0
                ]  # drop uncertainties, so far, there's no use cases for them
                value = value_type(value)
            else:
                value = value_type()
        return label, value

    def _reducer(_: Any, line: str) -> None:
        line = line.strip()
        if not line or line.startswith("#"):
            return
        label, value = _split_line(line)
        dst = collector.get(label, None)
        if dst is not None:
            dst.append(value)

    with path.open(encoding="utf-8") as fid:
        reduce(_reducer, fid.readlines(), None)

    symbols = list(
        cast(
            str,
            map(lambda x: "H" if x in ["D", "T"] else x, collector["atomic_symbol"]),
        )
    )
    collector["atomic_symbol"] = symbols
    atomic_numbers = collector["atomic_number"]
    symbol_2_atomic_number = dict(zip(symbols, atomic_numbers))
    atomic_number_2_symbol = dict(zip(atomic_numbers, symbols))
    table = pd.DataFrame.from_dict(collector)
    table.set_index(
        ["atomic_number", "mass_number"], inplace=True, verify_integrity=True
    )
    table.index.name = "atom_mass"

    return symbol_2_atomic_number, atomic_number_2_symbol, table


SYMBOL_2_ATOMIC_NUMBER, ATOMIC_NUMBER_2_SYMBOL, NUCLIDES_TABLE = _load_tables()


@dataclass
class Nuclide(Element):
    """Accessor to the Nuclide information."""

    mass_number: int

    def __post_init__(self, element: Union[int, str]) -> None:
        """Pass the symbol or atomic number (Z) to parent Element.

        Args:
            element: either symbol or atomic number to define the Element.
        """
        super(Nuclide, self).__post_init__(element)

    @property
    def a(self) -> int:
        """Synonym to mass number.

        Returns:
            The mass number (A) of the Nuclide.
        """
        return self.mass_number

    def _key(self) -> Tuple[int, int]:
        return self.atomic_number, self.mass_number

    @property
    def relative_atomic_mass(self) -> float:
        """The isotope mass (a.u.).

        Returns:
            The nuclide mass (a.u.).
        """
        return cast(float, NUCLIDES_TABLE.loc[self._key()].relative_atomic_mass)

    @property
    def isotopic_composition(self) -> float:
        """Natural presence of nuclide (fraction of atoms in Element).

        Returns:
            float: fraction of atoms of this nuclide.
        """
        return cast(float, NUCLIDES_TABLE.loc[self._key()].isotopic_composition)

    # @classmethod
    # def from_dict(cls, data: Dict) -> "Nuclide":
    #     """Helper to retrieve a Nuclide from JSON."""
    #     return cls(data["atomic_number"], mass_number=data["mass_number"])


@dispatch(int, int)
def get_atomic_mass(atomic_number: int, mass_number: int) -> float:
    """Retrieve atomic mass for a nuclide by atomic and mass numbers, a.u.

    Args:
        atomic_number: Z of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide by its atomic and mass numbers.
    """
    return NUCLIDES_TABLE.loc[(atomic_number, mass_number)]["relative_atomic_mass"]


@dispatch(str, int)  # type: ignore[no-redef]
def get_atomic_mass(symbol: str, mass_number: int) -> float:  # noqa: F811
    """Retrieve atomic mass for a nuclide by symbol and mass number, a.u.

    Args:
        symbol: symbol of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide by its symbol and mass numbers.
    """
    atomic_number = SYMBOL_2_ATOMIC_NUMBER[symbol]
    return get_atomic_mass(atomic_number, mass_number)


# TODO dvp: implement abundance functionality using the NIST data in this module
