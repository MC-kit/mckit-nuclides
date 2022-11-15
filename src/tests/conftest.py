from typing import Generator

import os

from pathlib import Path

import pytest

from mckit_nuclides.utils.resource import path_resolver


@pytest.fixture(scope="session")
def data() -> Path:
    """Path to test data"""
    return path_resolver("tests")("data")


@pytest.fixture
def cd_tmpdir(tmpdir) -> Generator[None, None, None]:
    """Switch to temp dir for a test run."""
    old_dir = tmpdir.chdir()
    try:
        yield
    finally:
        os.chdir(old_dir)
