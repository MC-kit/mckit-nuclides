"""Information on nuclides: masses, natural presence and more."""
from __future__ import annotations

from typing import Any, Dict, Final, List, Tuple, cast

import pandas as pd

from mckit_nuclides.elements import TABLE_VALUE_TYPE, z
from mckit_nuclides.utils.resource import path_resolver

_TYPES: Final = {
    "atomic_number": int,
    "mass_number": int,
    "relative_atomic_mass": float,
    "isotopic_composition": float,
}


def _split_line(_line: str) -> Tuple[str, Any]:
    _label, _value = map(str.strip, _line.split("="))  # type: str, str
    _label = _label.lower().replace(" ", "_")
    value_type = _TYPES.get(_label, None)
    if value_type is not None:
        if _value:
            # drop uncertainties, so far, there's no use cases for them
            _value = _value.split("(", 1)[0]
            _value = value_type(_value)
        else:
            _value = value_type()
    return _label, _value


def _load_tables() -> pd.DataFrame:
    collector = _load_nist_file()
    symbols = ["H" if x in ["D", "T"] else x for x in collector["atomic_symbol"]]
    collector["atomic_symbol"] = symbols
    nuclides_table = pd.DataFrame.from_dict(collector)
    nuclides_table = nuclides_table.set_index(
        ["atomic_number", "mass_number"], verify_integrity=True
    )
    # TODO dvp: There's an important exclusion with Ta180.
    #           It's "observationally stable" only in metastable state
    #           (https://en.wikipedia.org/wiki/Isotopes_of_tantalum).
    #           Should we add add additional sub index for 'state' for
    #           this only exclusion?
    #           Or we'd better to supply this information on compositions specs?
    nuclides_table.index.name = "atom_and_mass_numbers"
    nuclides_table = nuclides_table.rename(
        columns={"atomic_symbol": "symbol", "relative_atomic_mass": "nuclide_mass"},
    )

    return nuclides_table


def _load_nist_file() -> Dict[str, List[Any]]:
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
    with path.open(encoding="utf-8") as fid:
        for line in fid.readlines():
            line = line.strip()
            if line and not line.startswith("#"):
                label, value = _split_line(line)
                dst = collector.get(label, None)
                if dst is not None:
                    dst.append(value)
    return collector


NUCLIDES_TABLE = _load_tables()

# TODO dvp: improve table, add uncertainties and more nuclide properties:
#           half-life, decay mode, etc.


def get_property(
    z_or_symbol: int | str, mass_number: int, column: str
) -> TABLE_VALUE_TYPE:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        z_or_symbol: Z or symbol of a nuclide
        mass_number: A
        column: name of column to extract value from

    Returns:
        Value of a culumn for a given nuclide.
    """
    if isinstance(z_or_symbol, str):
        z_or_symbol = z(z_or_symbol)
    return cast(TABLE_VALUE_TYPE, NUCLIDES_TABLE.at[(z_or_symbol, mass_number), column])


def get_nuclide_mass(z_or_symbol: int | str, mass_number: int) -> float:
    """Retrieve mass of a nuclide by atomic and mass numbers, a.u.

    Args:
        z_or_symbol: Z or symbol of a nuclide
        mass_number: A

    Returns:
        Mass of the Nuclide (a.u).
    """
    return cast(float, get_property(z_or_symbol, mass_number, "nuclide_mass"))
