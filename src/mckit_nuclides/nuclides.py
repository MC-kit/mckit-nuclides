"""Information on nuclides: masses, natural presence and more."""

from typing import Any, Dict, List, Tuple, Union

from dataclasses import dataclass

import pandas as pd

from mckit_nuclides.elements import Element
from mckit_nuclides.utils.resource import path_resolver
from multipledispatch import dispatch


def _load_tables() -> Tuple[Dict[str, int], Dict[int, str], pd.DataFrame]:
    path = path_resolver("mckit_nuclides")(
        "data/nist_atomic_weights_and_element_compositions.txt"
    )

    collector: Dict[str, List[Any]] = {
        "atomic_number": [],
        "atomic_symbol": [],
        "mass_number": [],
        "relative_atomic_mass": [],
        "isotopic_composition": [],
    }

    types = {
        "atomic_number": int,
        "mass_number": int,
        "relative_atomic_mass": float,
        "isotopic_composition": float,
    }

    # noinspection PyTypeChecker
    def _split_line(_line: str) -> Tuple[str, Any]:
        _label, _value = map(str.strip, _line.split("="))  # type: str, str
        _label = _label.lower().replace(" ", "_")
        value_type = types.get(_label, None)
        if value_type is not None:
            if _value:
                # drop uncertainties, so far, there's no use cases for them
                _value = _value.split("(", 1)[0]
                _value = value_type(_value)
            else:
                _value = value_type()
        return _label, _value

    with path.open(encoding="utf-8") as fid:
        for line in fid.readlines():
            line = line.strip()
            if line and not line.startswith("#"):
                label, value = _split_line(line)
                dst = collector.get(label, None)
                if dst is not None:
                    dst.append(value)

    symbols = ["H" if x in ["D", "T"] else x for x in collector["atomic_symbol"]]
    collector["atomic_symbol"] = symbols
    atomic_numbers = collector["atomic_number"]
    symbol_2_atomic_number = dict(zip(symbols, atomic_numbers))
    atomic_number_2_symbol = dict(zip(atomic_numbers, symbols))
    table = pd.DataFrame.from_dict(collector)
    table.set_index(
        ["atomic_number", "mass_number"], inplace=True, verify_integrity=True
    )
    # TODO dvp: There's an important exclusion with Ta180.
    #           It's "observationally stable" only in metastable state
    #           (https://en.wikipedia.org/wiki/Isotopes_of_tantalum).
    #           Should we add add additional sub index for 'state' for
    #           this only exclusion?
    #           Or we'd better to supply this information on compositions specs?
    table.index.name = "atom_and_mass_numbers"
    table.rename(
        columns={"atomic_symbol": "symbol", "relative_atomic_mass": "nuclide_mass"},
        inplace=True,
    )

    return symbol_2_atomic_number, atomic_number_2_symbol, table


SYMBOL_2_ATOMIC_NUMBER, ATOMIC_NUMBER_2_SYMBOL, NUCLIDES_TABLE = _load_tables()

# TODO dvp: improve table, add uncertainties and more nuclide properties:
#           half-life, decay mode, etc.


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

    def __getattr__(self, item):  # type: ignore[no-untyped-def]
        """Use columns of NUCLIDES_TABLE as properties of the Element accessor.

        The `column` can be anything selecting a column or columns
        from NUCLIDES_TABLE and ELEMENTS_TABLE, but not from both.

        Args:
            item: column or columns of NUCLIDES_TABLE

        Returns:
            content selected for this Nuclide instance.
        """
        try:
            return super(Nuclide, self).__getattr__(item)  # type: ignore[no-untyped-call]
        except KeyError:
            return NUCLIDES_TABLE.loc[self._key()][item]


@dispatch(int, int)
def get_nuclide_mass(atomic_number: int, mass_number: int) -> float:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        atomic_number: Z of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide by its atomic and mass numbers (a.u).
    """
    return NUCLIDES_TABLE.loc[(atomic_number, mass_number)]["nuclide_mass"]


@dispatch(str, int)  # type: ignore[no-redef]
def get_nuclide_mass(symbol: str, mass_number: int) -> float:  # noqa: F811
    """Retrieve mass of a nuclide by symbol and mass number, a.u.

    Args:
        symbol: symbol of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide by its symbol and mass numbers.
    """
    atomic_number = SYMBOL_2_ATOMIC_NUMBER[symbol]
    return get_nuclide_mass(atomic_number, mass_number)
