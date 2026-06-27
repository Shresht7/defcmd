from defcmd.ansi import ANSICode, ANSICodes, ANSIColorCode, compose, reset, bold, dim, italic, underline, inverse, invisible, inverse, strikethrough, black, red, green, yellow, blue, magenta, cyan, white, default

# ---------
# ANSI CODE
# ---------

def test_ansi_code_str():
    code = ANSICode(31)
    assert str(code) == "\x1b[31m"

def test_ansi_code_repr():
    code = ANSICode(31)
    assert repr(code) == "ANSICode(31)"

def test_ansi_code_unset():
    code = ANSICode(31, unset_code=39)
    assert code.unset_code == 39
    assert code.unset == "\x1b[39m"

def test_ansi_code_wrap():
    code = ANSICode(31)
    text = "Hello"
    assert code.wrap(text) == "\x1b[31mHello\x1b[0m"

def test_ansi_code_wrap_with_unset():
    code = ANSICode(32, unset_code=39)
    text = "Hello"
    assert code.wrap(text) == "\x1b[32mHello\x1b[39m"

def test_ansi_code_call():
    code = ANSIColorCode(31)
    text = "Hello"
    assert code(text) == "\x1b[31mHello\x1b[39m"

def test_ansi_code_bg():
    code = ANSIColorCode(31)
    assert str(code.bg) == "\x1b[41m"

def test_ansi_code_bright():
    code = ANSIColorCode(31)
    assert str(code.bright) == "\x1b[91m"

def test_ansi_code_bg_bright():
    code = ANSIColorCode(31)
    assert str(code.bg.bright) == "\x1b[101m"

def test_ansi_code_bg_bright_wrap():
    code = ANSIColorCode(31)
    text = "Hello"
    assert code.bg.bright.wrap(text) == "\x1b[101mHello\x1b[109m"

# ----------
# ANSI CODES
# ----------

def test_ansi_codes_str():
    codes = ANSICodes(31, 1)
    assert str(codes) == "\x1b[31;1m"

def test_ansi_codes_repr():
    codes = ANSICodes(31, 1)
    assert repr(codes) == "ANSICodes(ANSICode(31), ANSICode(1))"

def test_ansi_codes_wrap():
    codes = ANSICodes(31, 1)
    text = "Hello"
    assert codes.wrap(text) == "\x1b[31;1mHello\x1b[0m"

def test_ansi_codes_wrap_multiple():
    codes = ANSICodes(31, 1, 4)
    text = "Hello"
    assert codes.wrap(text) == "\x1b[31;1;4mHello\x1b[0m"

def test_ansi_codes_call():
    codes = ANSICodes(31, 1)
    text = "Hello"
    assert codes(text) == "\x1b[31;1mHello\x1b[0m"

def test_ansi_codes_add():
    codes = ANSICodes(31)
    codes.add(1)
    assert str(codes) == "\x1b[31;1m"

def test_ansi_codes_add_multiple():
    codes = ANSICodes(31)
    codes.add(1, 4, ANSICode(7))
    assert str(codes) == "\x1b[31;1;4;7m"

# -----
# USAGE
# -----

def test_reset():
    assert str(reset) == "\x1b[0m"

def test_styles():
    assert str(bold) == "\x1b[1m"
    assert str(dim) == "\x1b[2m"
    assert str(italic) == "\x1b[3m"
    assert str(underline) == "\x1b[4m"
    assert str(inverse) == "\x1b[7m"
    assert str(invisible) == "\x1b[8m"
    assert str(strikethrough) == "\x1b[9m"

def test_colors():
    assert str(black) == "\x1b[30m"
    assert str(red) == "\x1b[31m"
    assert str(green) == "\x1b[32m"
    assert str(yellow) == "\x1b[33m"
    assert str(blue) == "\x1b[34m"
    assert str(magenta) == "\x1b[35m"
    assert str(cyan) == "\x1b[36m"
    assert str(white) == "\x1b[37m"
    assert str(default) == "\x1b[39m"

def test_color_bg():
    assert str(black.bg) == "\x1b[40m"
    assert str(red.bg) == "\x1b[41m"
    assert str(green.bg) == "\x1b[42m"
    assert str(yellow.bg) == "\x1b[43m"
    assert str(blue.bg) == "\x1b[44m"
    assert str(magenta.bg) == "\x1b[45m"
    assert str(cyan.bg) == "\x1b[46m"
    assert str(white.bg) == "\x1b[47m"

def test_color_bright():
    assert str(black.bright) == "\x1b[90m"
    assert str(red.bright) == "\x1b[91m"
    assert str(green.bright) == "\x1b[92m"
    assert str(yellow.bright) == "\x1b[93m"
    assert str(blue.bright) == "\x1b[94m"
    assert str(magenta.bright) == "\x1b[95m"
    assert str(cyan.bright) == "\x1b[96m"
    assert str(white.bright) == "\x1b[97m"

def test_color_bg_bright():
    assert str(black.bg.bright) == "\x1b[100m"
    assert str(red.bg.bright) == "\x1b[101m"
    assert str(green.bg.bright) == "\x1b[102m"
    assert str(yellow.bg.bright) == "\x1b[103m"
    assert str(blue.bg.bright) == "\x1b[104m"
    assert str(magenta.bg.bright) == "\x1b[105m"
    assert str(cyan.bg.bright) == "\x1b[106m"
    assert str(white.bg.bright) == "\x1b[107m"

def test_compose_class():
    codes = ANSICodes(bold, red, underline)
    text = "Hello"
    assert str(codes) == "\x1b[1;31;4m"
    assert codes.wrap(text) == "\x1b[1;31;4mHello\x1b[0m"

def test_compose_function():
    stylish = compose(bold, red, underline)
    text = "Hello"
    assert str(stylish) == "\x1b[1;31;4m"
    assert stylish(text) == "\x1b[1;31;4mHello\x1b[0m"
