from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser

def deploy(host: str, port: int = 8080):
    pass

params = inspect_function_signature(deploy)
parser = build_parser(params)
ns = parser.parse_args(["localhost"])
print(ns.host, ns.port)

ns2 = parser.parse_args(["localhost", "--port", "9090"])
print(ns2.host, ns2.port, type(ns2.port))
