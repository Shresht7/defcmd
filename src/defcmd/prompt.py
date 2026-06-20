from __future__ import annotations

from defcmd.introspect import Parameter

def prompt_for_param(param: Parameter, input_fn=input):

    # Prompt the user for input until they provide a non-blank value
    # or, if the parameter is optional, they hit Enter to accept the default value
    while True:

        # Use the parameter name and type annotation to create a helpful prompt message
        raw = input_fn(f"Enter value for {param.name} ({param.annotation.__name__}): ")

        if raw == "":
            # If the user provided blank input, but the parameter is required, we need to prompt again
            if param.required:
                print(f"{param.name} is required. Please enter a value.")
                continue
            # If the user provided blank input and the parameter is optional, we can return the default value
            else:
                return param.default
        
        # If the parameter is a boolean, we can accept a variety of common inputs to represent true and false values
        if param.annotation is bool:
            if raw.lower() in ["true", "yes", "y", "1"]:
                return True
            elif raw.lower() in ["false", "no", "n", "0"]:
                return False
            else:
                print("Please enter a valid boolean value (true/false, yes/no, y/n, 1/0)")
                continue
                
        return raw
