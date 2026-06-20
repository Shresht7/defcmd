from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser

def log(host: str, verbose: bool = False):
    pass

params = inspect_function_signature(log)
parser = build_parser(params)
print(parser.parse_args(["localhost"]).verbose)
print(parser.parse_args(["localhost", "--verbose"]).verbose)
print(parser.parse_args(["localhost", "--no-verbose"]).verbose)
