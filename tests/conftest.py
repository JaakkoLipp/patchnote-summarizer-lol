import os
import sys
from pathlib import Path
import pytest


# Make backend importable regardless of cwd and allow utils to open local HTML files
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(autouse=True)
def _chdir_backend():
    """Run tests with cwd=backend so relative file reads work."""
    old = os.getcwd()
    os.chdir(str(BACKEND_DIR))
    try:
        yield
    finally:
        os.chdir(old)
