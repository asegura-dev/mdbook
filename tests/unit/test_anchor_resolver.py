"""Run the JavaScript anchor-resolver tests under Node, from pytest.

The resolver is the one part of the annotation feature that loses a reader's
work silently when it is wrong, so it gets real tests. They are JavaScript
because the code is, and Node's built-in runner needs no package.json and no
dependencies. Node is a development tool only: it is not required to build
mdbook, to open the generated HTML, or to run the executable, so a clone
without it skips this and keeps the rest of the suite green.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

JS_TESTS = sorted((Path(__file__).resolve().parents[1] / "js").glob("*.test.js"))
NODE = shutil.which("node")


def test_javascript_tests_exist() -> None:
    # Guards against the suite silently covering nothing if the folder moves.
    assert JS_TESTS, "no *.test.js found in tests/js"


@pytest.mark.skipif(NODE is None, reason="node is not installed; JS tests skipped")
def test_anchor_resolver_suite_passes() -> None:
    assert NODE is not None
    # Files are passed explicitly: Node's directory form does not resolve
    # reliably on Windows.
    result = subprocess.run(
        [NODE, "--test", *[str(path) for path in JS_TESTS]],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, f"\n{result.stdout}\n{result.stderr}"
