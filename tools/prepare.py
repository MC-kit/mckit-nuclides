"""Transform raw input data to parquet files to be used as resources in mckit-nuclides."""

from __future__ import annotations

from typing import Any, Final

from collections import OrderedDict
from pathlib import Path

import polars as pl

HERE = Path(__file__).parent
OUT = HERE.parent / "src/mckit_nuclides/data"

_ELEMENTS_SCHEMA: Final = OrderedDict(
    atomic_number=pl.UInt32,
    symbol=pl.String,
    name=pl.String,
    atomic_mass=pl.Float32,
    cpk_hec_color=pl.String,
    electron_configuration=pl.String,
    electron_negativity=pl.Float32,
    atomic_radius=pl.Float32,
    ionization_energy=pl.Float32,
    electron_affinity=pl.Float32,
    oxidation_states=pl.String,
    standard_state=pl.String,
    melting_point=pl.Float32,
    boiling_point=pl.Float32,
    density=pl.Float32,
    group_block=pl.String,
    year_discovered=pl.String,
    period=pl.UInt32,
    group=pl.UInt32,
)


_TYPES: Final = {
    "atomic_number": int,
    "mass_number": int,
    "relative_atomic_mass": float,
    "isotopic_composition": float,
}


def _make_elements_table(elements_csv: Path) -> pl.DataFrame:
    return pl.read_csv(elements_csv, schema=_ELEMENTS_SCHEMA).with_columns(
        pl.col("atomic_mass").alias("molar_mass"),
        pl.col("atomic_number").cast(pl.UInt8),  # read as UInt32 from the CSV - reduce memory size
        pl.col("period").cast(pl.UInt8),
        pl.col("group").cast(pl.UInt8),
    )


def _split_line(_line: str) -> tuple[str, Any]:
    _label, _value = map(str.strip, _line.split("="))  # type: str, str
    _label = _label.lower().replace(" ", "_")
    value_type = _TYPES.get(_label)
    if value_type is not None:
        if _value:
            # drop uncertainties, so far, there's no use cases for them
            _value = _value.split("(", 1)[0]
            _value = value_type(_value)
        else:
            _value = value_type()
    return _label, _value


def _load_nist_file(path: Path) -> dict[str, list[Any]]:
    collector: dict[str, list[Any]] = {
        "atomic_number": [],
        "atomic_symbol": [],
        "mass_number": [],
        "relative_atomic_mass": [],
        "isotopic_composition": [],
    }

    with path.open(encoding="utf-8") as fid:
        for line in fid.readlines():
            _line = line.strip()
            if _line and not _line.startswith("#"):
                label, value = _split_line(_line)
                dst = collector.get(label)
                if dst is not None:
                    dst.append(value)
    return collector


def _make_half_lives_table(half_lives_path: Path) -> pl.DataFrame:
    return pl.read_csv(half_lives_path).with_columns(
        pl.when(pl.col("m").eq("M")).then(1).otherwise(0).cast(pl.UInt8).alias("state")
    )


def _make_nist_table(half_lives: pl.DataFrame, nist_file_path: Path) -> pl.DataFrame:
    collector = _load_nist_file(nist_file_path)
    symbols = ["H" if x in ["D", "T"] else x for x in collector["atomic_symbol"]]
    collector["atomic_symbol"] = symbols
    return (
        pl.DataFrame(collector)
        # Augment with information on state, correct for Ta180 - it's observable in modified state
        .with_columns(
            pl.when(pl.col("atomic_number").eq(73) & pl.col("mass_number").eq(180))
            .then(1)
            .otherwise(0)
            .cast(pl.UInt8)
            .alias("state")
        )
        .join(
            half_lives,
            left_on=("atomic_number", "mass_number", "state"),
            right_on=["z", "a", "state"],
            how="left",
        )
        .select(
            pl.col("atomic_number").cast(pl.UInt8),
            pl.col("mass_number").cast(pl.UInt16),
            pl.col("state").cast(pl.UInt8),
            pl.col("relative_atomic_mass").cast(pl.Float32).alias("molar_mass"),
            pl.col("isotopic_composition").cast(pl.Float32),
            pl.col("half_life"),
        )
    )


if __name__ == "__main__":
    _make_elements_table(HERE / "data/elements.csv").write_parquet(OUT / "elements.parquet")
    _make_nist_table(
        _make_half_lives_table(HERE / "data/half-lives.csv"),
        HERE / "data/nist_atomic_weights_and_element_compositions.txt",
    ).write_parquet(OUT / "nuclides.parquet")
