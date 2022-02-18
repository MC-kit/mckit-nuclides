#!python
"""Clear environment from the old .dist-info packages.

This fixes https://github.com/python-poetry/poetry/issues/4526.
Should be fixed in poetry 1.2, but it's not available yet.
Run this if test_package() fails on pytest run.

"""
from typing import Optional, TypeVar

import platform
import shutil
import subprocess  # noqa
import sys

from pathlib import Path

import tomli

PathLike = TypeVar("PathLike", str, Path)


def search_upwards_for_file(filename: PathLike) -> Optional[Path]:
    """Search upward from the current directory for a `filename`.

    Args:
        filename: the file name to look for if available.

    Returns:
        Path: the location of the first file found or None, if none was found
    """
    d = Path.cwd()
    root = Path(d.root)

    while d != root:
        attempt = d / filename
        if attempt.exists():
            return attempt
        d = d.parent

    return None


def get_project_name() -> str:
    """Find project name, which is prefix for info distributions.

    Returns:
        str: the name of package specified in pyproject.toml

    Raises:
        EnvironmentError: if file pyproject.toml is not found.
    """
    pyproject_path = search_upwards_for_file("pyproject.toml")
    if pyproject_path is None:
        raise EnvironmentError(
            "Illegal directory: cannot find file pyproject.toml "
            f"from current directory: {Path.cwd()}"
        )
    pyproject = tomli.loads(pyproject_path.read_text())
    name = pyproject["tool"]["poetry"]["name"].replace("-", "_")
    print(f"Package {name} is found in {pyproject_path.absolute()}")
    return name


def get_packages_dir() -> Path:
    """Define packages location depending on system.

    Returns:
        Path: to directory 'site-packages' containing distributions info folders.

    Raises:
        EnvironmentError: if there's no directory 'site-packages'.
    """
    system = platform.system()
    if system == "Windows":
        site_packages = Path("Lib", "site-packages")
    else:
        python = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = Path("lib", python, "site-packages")
    result = Path(sys.prefix, site_packages)
    if not result.is_dir():
        raise EnvironmentError(
            f"Cannot find site package for system {system} in folder {result}"
        )
    return result


def clear_previous_distributions_info() -> None:
    """Remove all dist-info folders from previous installations."""
    packages_dir = get_packages_dir()
    name = get_project_name()
    dists = list(packages_dir.glob(f"{name}-*.dist-info"))
    if dists:
        for dist in dists:
            print("Removing distribution", dist)
            shutil.rmtree(dist)
    else:
        print("Nothing to remove for package", name)


def run_poetry_install() -> None:
    """Refresh installation of the package."""
    print("Running `poetry install`.")
    subprocess.run(["poetry", "install"])  # noqa


if __name__ == "__main__":
    clear_previous_distributions_info()
    run_poetry_install()
