from __future__ import annotations

from typing import Generator

import importlib.resources as rc
import os

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def data() -> Path:
    """Path to test data.

    Returns:
        Path: path to test data
    """
    return rc.files("tests").joinpath("data")


@pytest.fixture()
def cd_tmpdir(tmp_path: Path) -> Generator[Path, None, None]:
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
