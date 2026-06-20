from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser

def deploy(host: str):
    pass

params = inspect_function_signature(deploy)
parser = build_parser(params)
ns = parser.parse_args(["myhost"])
print(ns.host)
