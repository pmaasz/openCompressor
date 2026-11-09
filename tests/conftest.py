"""Pytest/unittest test configuration for headless CI (gh #19)."""

import os

# Force non-interactive matplotlib backend before any test imports pyplot.
os.environ.setdefault("MPLBACKEND", "Agg")
# Headless Qt for widget tests in CI.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    import matplotlib

    matplotlib.use("Agg", force=True)
except Exception:
    pass
