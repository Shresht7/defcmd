from defcmd.introspect import inspect_function_signature
from defcmd.prompt import prompt_for_param
from typing import Literal

def deploy(env: Literal["dev", "prod"] = "dev"):
    pass

[p] = inspect_function_signature(deploy)
print(prompt_for_param(p))
