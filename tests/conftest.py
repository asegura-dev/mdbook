"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def sample_files() -> list[Path]:
    """The sample .md files, in order (volume1, volume2)."""
    return [DATA_DIR / "volume1.md", DATA_DIR / "volume2.md"]
