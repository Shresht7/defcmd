from defcmd.introspect import inspect_function_signature
from defcmd.prompt import prompt_for_param

def deploy(verbose: bool):
    pass

[p] = inspect_function_signature(deploy)
print(prompt_for_param(p))
