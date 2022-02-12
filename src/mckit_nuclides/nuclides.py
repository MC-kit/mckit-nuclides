from typing import Dict

from dataclasses import InitVar, dataclass, field
from functools import reduce

import pandas as pd

from multipledispatch import dispatch
from mckit_nuclides.utils.resource import path_resolver


def load_tables():
    path = path_resolver("mckit_nuclides")(
        "data/nist_atomic_weights_and_element_compositions.txt"
    )

    collector = dict(
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
    def split_line(line: str):
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

    def reducer(_, line: str):
        line = line.strip()
        if not line or line.startswith("#"):
            return
        label, value = split_line(line)
        dst = collector.get(label, None)
        if dst is not None:
            dst.append(value)

    with path.open(encoding="utf-8") as fid:
        reduce(reducer, fid.readlines(), None)

    symbols = list(
        map(lambda x: "H" if x in ["D", "T"] else x, collector["atomic_symbol"])
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


SYMBOL_2_ATOMIC_NUMBER, ATOMIC_NUMBER_2_SYMBOL, NUCLIDES_TABLE = load_tables()


@dataclass
class Nuclide:
    element: InitVar
    atomic_number: int = field(init=False)
    symbol: str = field(init=False)
    mass_number: int

    def __post_init__(self, element):
        if isinstance(element, str):
            self.atomic_number = SYMBOL_2_ATOMIC_NUMBER[element]
            self.symbol = element
        elif isinstance(element, int):
            self.atomic_number = element
            self.symbol = ATOMIC_NUMBER_2_SYMBOL[element]

    @property
    def z(self):
        return self.atomic_number

    @property
    def a(self):
        return self.mass_number

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(data["atomic_number"], mass_number=data["mass_number"])


@dispatch(int, int)
def get_atomic_mass(atomic_number: int, mass_number: int) -> float:
    return NUCLIDES_TABLE.loc[(atomic_number, mass_number)]["relative_atomic_mass"]


@dispatch(str, int)
def get_atomic_mass(symbol: str, mass_number: int) -> float:
    atomic_number = SYMBOL_2_ATOMIC_NUMBER[symbol]
    return get_atomic_mass(atomic_number, mass_number)


@dispatch(Nuclide)
def get_atomic_mass(_nuclide: Nuclide) -> float:
    return get_atomic_mass(_nuclide.z, _nuclide.a)


# TODO dvp: implement abundance functionality using the NIST data in this module


@dispatch(int, int)
def nuclide(atomic_number: int, mass_number: int) -> Nuclide:
    # noinspection PyTypeChecker
    return Nuclide(atomic_number, mass_number)


@dispatch(str, int)
def nuclide(symbol: str, mass_number: int) -> Nuclide:
    atomic_number = SYMBOL_2_ATOMIC_NUMBER[symbol]
    return nuclide(atomic_number, mass_number)
