from __future__ import annotations

from typing import TYPE_CHECKING

import importlib.resources as rc
import os

from pathlib import Path

if TYPE_CHECKING:
    from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def data() -> Generator[Path]:
    """Path to test data.

    Yields:
        path to test data
    """
    with rc.as_file(rc.files("tests").joinpath("data")) as path:
        yield path


@pytest.fixture()
def cd_tmpdir(tmp_path: Path) -> Generator[Path]:
    """Switch to temp dir for a test run.

    Yields:
        Path: to temp directory
    """
    old_dir = Path.cwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(old_dir)
