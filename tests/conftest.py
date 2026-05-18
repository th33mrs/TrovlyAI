"""Shared pytest fixtures for the Trovly test suite."""

import sys
from pathlib import Path

import pytest

# Make the project root importable so `import auth` works from tests/.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolated_users_dir(tmp_path, monkeypatch):
    """Each test runs in a fresh tmp cwd so users.json never leaks."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def fast_bcrypt(monkeypatch):
    """bcrypt rounds=4 keeps the suite fast — 12 is overkill for tests."""
    import auth

    monkeypatch.setattr(auth, "BCRYPT_ROUNDS", 4)
