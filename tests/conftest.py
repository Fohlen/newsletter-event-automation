from pathlib import Path
import pytest

_SCRIPT_DIR = Path(__file__).parent


@pytest.fixture
def data_dir():
    return _SCRIPT_DIR / "data"
