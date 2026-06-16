"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture
def sample_files() -> list[Path]:
    """The example .md files (the clean-architecture guide), in order."""
    return sorted(EXAMPLES_DIR.glob("*.md"))
