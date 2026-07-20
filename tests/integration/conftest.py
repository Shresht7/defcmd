import pytest
from defcmd.terminal import is_ansi_enabled, set_ansi_enabled


@pytest.fixture(autouse=True)
def _preserve_ansi():
    saved = is_ansi_enabled()
    yield
    set_ansi_enabled(saved)
