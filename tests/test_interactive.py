from defcmd.interactive import is_interactive

def test_empty_argv_and_tty_is_interactive():
    assert is_interactive([], isatty=lambda: True) is True


def test_empty_argv_but_not_tty_is_not_interactive():
    assert is_interactive([], isatty=lambda: False) is False


def test_nonempty_argv_is_not_interactive():
    assert is_interactive(["--host", "x"], isatty=lambda: True) is False
