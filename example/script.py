from typing import Literal
from defcmd.introspect import inspect_function_signature
from defcmd.argparser import build_parser

def deploy(env: Literal["dev", "prod"] = "dev"):
    pass

params = inspect_function_signature(deploy)
parser = build_parser(params)
print(parser.parse_args([]).env)
print(parser.parse_args(["--env", "prod"]).env)
parser.parse_args(["--env", "staging"]) # Error
