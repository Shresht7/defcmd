from defcmd.introspect import inspect_function_signature
from defcmd.interactive import is_interactive

def example_function(name: str, age: int = 30, verbose: bool = False) -> None:
    """Example function to demonstrate introspection"""
    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Verbose: {verbose}")

if __name__ == "__main__":
    print("Is interactive:", is_interactive([]))  # Check if running in interactive mode
    print("Is interactive:", is_interactive(['arg1']))  # Check if running in interactive mode with arguments
    parameters = inspect_function_signature(example_function)
    for param in parameters:
        print(param)
