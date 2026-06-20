from defcmd.runner import cmd

@cmd
def greet(name: str, times: int = 1, excited: bool = False):
    """Greet a person a specified number of times, optionally with excitement."""
    greeting = f"Hello, {name}!"
    if excited:
        greeting = greeting.upper() + "!!!"
    for _ in range(times):
        print(greeting)

if __name__ == "__main__":
    greet.run()
