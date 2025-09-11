"""Yes, we check constants here."""

from __future__ import annotations

import pytest

from mckit_nuclides.constants import ATOMIC_MASS_CONSTANT, AVOGADRO


def test_constants() -> None:
    assert pytest.approx(1.0, abs=2e-9) == ATOMIC_MASS_CONSTANT * 1000.0 * AVOGADRO
