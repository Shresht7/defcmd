from defcmd.terminal.keypress import read_keypress, raw_mode, KEY_MAP, CSI_KEY_MAP


def test_read_keypress_regular_char():
    assert read_keypress(inject="a") == "a"


def test_read_keypress_enter():
    assert read_keypress(inject="\r") == "enter"


def test_read_keypress_newline():
    assert read_keypress(inject="\n") == "enter"


def test_read_keypress_tab():
    assert read_keypress(inject="\t") == "tab"


def test_read_keypress_space():
    assert read_keypress(inject=" ") == "space"


def test_read_keypress_backspace_del():
    assert read_keypress(inject="\x7f") == "backspace"


def test_read_keypress_backspace_bs():
    assert read_keypress(inject="\b") == "backspace"


def test_read_keypress_ctrl_c():
    assert read_keypress(inject="\x03") == "ctrl+c"


def test_read_keypress_ctrl_d():
    assert read_keypress(inject="\x04") == "ctrl+d"


def test_read_keypress_escape():
    assert read_keypress(inject="\x1b") == "escape"


def test_read_keypress_arrow_up():
    assert read_keypress(inject="\x1b[A") == "up"


def test_read_keypress_arrow_down():
    assert read_keypress(inject="\x1b[B") == "down"


def test_read_keypress_arrow_right():
    assert read_keypress(inject="\x1b[C") == "right"


def test_read_keypress_arrow_left():
    assert read_keypress(inject="\x1b[D") == "left"


def test_read_keypress_home():
    assert read_keypress(inject="\x1b[H") == "home"


def test_read_keypress_end():
    assert read_keypress(inject="\x1b[F") == "end"


def test_read_keypress_digit():
    assert read_keypress(inject="5") == "5"


def test_read_keypress_uppercase():
    assert read_keypress(inject="Q") == "Q"


def test_read_keypress_symbol():
    assert read_keypress(inject="-") == "-"


def test_raw_mode_is_context_manager():
    with raw_mode():
        pass


def test_all_key_map_entries():
    for raw, expected in KEY_MAP.items():
        assert read_keypress(inject=raw) == expected


def test_all_csi_key_map_entries():
    for letter, expected in CSI_KEY_MAP.items():
        seq = f"\x1b[{letter}"
        assert read_keypress(inject=seq) == expected
