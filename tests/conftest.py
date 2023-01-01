from typing import Generator

import os

from pathlib import Path

import pytest

from mckit_nuclides.utils.resource import path_resolver


@pytest.fixture(scope="session")
def data() -> Path:
    """Path to test data.

    Returns:
        Path: path to test data
    """
    return path_resolver("tests")("data")


@pytest.fixture
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
