"""Fixtures compartidas por los tests."""

from __future__ import annotations

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def sample_files() -> list[Path]:
    """Los .md de ejemplo, en orden (tomo1, tomo2)."""
    return [DATA_DIR / "tomo1.md", DATA_DIR / "tomo2.md"]
