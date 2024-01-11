"""Transform raw input data to parquet files to be used as resources."""
from __future__ import annotations
from typing import Any, Final

from pathlib import Path

import polars as pl

HERE = Path(__file__).parent

_TYPES: Final = {
    "atomic_number": int,
    "mass_number": int,
    "relative_atomic_mass": float,
    "isotopic_composition": float,
}


def _transform_elements():
    src = HERE / "data/elements.csv"
    dst = HERE.parent / "mckit_nuclides/data/elements.parquet"
    pl.read_csv(src).write_parquet(dst)
    print(f"Saved elements file {dst}")


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


def _load_nist_file() -> dict[str, list[Any]]:
    collector: dict[str, list[Any]] = {
        "atomic_number": [],
        "atomic_symbol": [],
        "mass_number": [],
        "relative_atomic_mass": [],
        "isotopic_composition": [],
    }
    path = HERE / "data/nist_atomic_weights_and_element_compositions.txt"
    with path.open(encoding="utf-8") as fid:
        for line in fid.readlines():
            _line = line.strip()
            if _line and not _line.startswith("#"):
                label, value = _split_line(_line)
                dst = collector.get(label)
                if dst is not None:
                    dst.append(value)
    return collector


def _make_nist_table() -> pl.DataFrame:
    half_lives = pl.read_csv(HERE / "data/half-lives.csv").with_columns(
        pl.when(pl.col("m").eq("M")).then(1).otherwise(0).cast(pl.Int8).alias("state"),
    )
    collector = _load_nist_file()
    symbols = ["H" if x in ["D", "T"] else x for x in collector["atomic_symbol"]]
    collector["atomic_symbol"] = symbols
    return (
        pl.DataFrame(collector)
        # Augment with information on state, correct fot Ta180 - it's observable in modified state
        .with_columns(
            pl.when(pl.col("atomic_number").eq(73) & pl.col("mass_number").eq(180))
            .then(1)
            .otherwise(0)
            .cast(pl.Int8)
            .alias("state"),
        )
        .join(
            half_lives,
            left_on=("atomic_number", "mass_number", "state"),
            right_on=["z", "a", "state"],
        )
        .select(
            pl.col("atomic_number").cast(pl.Int8),
            pl.col("mass_number").cast(pl.Int16),
            pl.col("state").cast(pl.Float32),
            pl.col("relative_atomic_mass").cast(pl.Float32),
            pl.col("isotopic_composition").cast(pl.Float32),
            pl.col("half_life"),
        )
    )


def _transform_nuclides():
    dst = HERE.parent / "mckit_nuclides/data/nuclides.parquet"
    _make_nist_table().write_parquet(dst)
    print("Saved nuclides file", dst)


if __name__ == "__main__":
    _transform_elements()
    _transform_nuclides()
