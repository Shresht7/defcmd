from defcmd.introspect import inspect_function_signature
from defcmd.prompt import prompt_for_param

def deploy(host: str):
    pass

[param] = inspect_function_signature(deploy)
value = prompt_for_param(param)
print(f"got: {value!r}")
