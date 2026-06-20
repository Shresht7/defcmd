from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser

def test_required_str_becomes_positional_argument():
    def f(name: str):
        pass

    params = inspect_function_signature(f)
    parser = build_parser(params)
    ns = parser.parse_args(["Alice"])
    assert ns.name == "Alice"
