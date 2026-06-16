# Regression tests

Convention: when we fix a bug, add a test here that fails with the bug present
and passes once it's fixed. Mark them with `@pytest.mark.regression` (or
`pytestmark = pytest.mark.regression` at module level) and name them after the
symptom, e.g. `test_fence_without_language_does_not_break.py`.

No regressions recorded yet.
