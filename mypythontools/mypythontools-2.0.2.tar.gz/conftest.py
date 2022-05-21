"""Runs before every pytest test. Used automatically (at least at VS Code)."""
from __future__ import annotations

import mypythontools_cicd as cicd

cicd.tests.setup_tests(matplotlib_test_backend=True)
