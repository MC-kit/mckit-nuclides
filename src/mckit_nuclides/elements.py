from typing import Dict, Union

from dataclasses import InitVar, dataclass, field

import pandas as pd

from mckit_nuclides.utils.resource import path_resolver
from multipledispatch import dispatch


def load_elements() -> pd.DataFrame:
    path = path_resolver("mckit_nuclides")("data/elements.csv")
    return pd.read_csv(path, index_col="Symbol")


ELEMENTS_TABLE = load_elements()


@dataclass
class Element:
    element: InitVar[Union[int, str]]
    atomic_number: int = field(init=False)

    def __post_init__(self, element: Union[int, str]) -> None:
        if isinstance(element, str):
            self.atomic_number = ELEMENTS_TABLE.loc[element]["AtomicNumber"]
        elif isinstance(element, int):
            self.atomic_number = element
        else:  # pragma nocover
            raise TypeError(f"Illegal parameter symbol {element}")

    @property
    def z(self):
        return self.atomic_number

    @property
    def name(self):
        return ELEMENTS_TABLE.iloc[self.atomic_number - 1]["Name"]

    @property
    def symbol(self):
        return ELEMENTS_TABLE.index[self.atomic_number - 1]

    @property
    def atomic_mass(self):
        return ELEMENTS_TABLE.iloc[self.atomic_number - 1]["AtomicMass"]

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(data["atomic_number"])


@dispatch(int)
def get_atomic_mass(atomic_number: int) -> float:
    return ELEMENTS_TABLE.iloc[atomic_number - 1]["AtomicMass"]


@dispatch(str)
def get_atomic_mass(symbol: str) -> float:
    return ELEMENTS_TABLE.loc[symbol]["AtomicMass"]
