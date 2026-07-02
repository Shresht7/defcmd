from defcmd import cmd, CLI

@cmd(
    description="Calculate with style",
    examples={
        "Add two numbers": "calc 1 + 2",
        "Subtract with decimals": "calc 10 - 3.5",
        "Multiply two numbers": "calc 2 '*' 3",
    },
    epilog="See the full docs at https://example.com/calc",
)
def calc(a: float, op: str, b: float):
    """Perform arithmetic operations on numbers."""
    result = eval(f"{a} {op} {b}")
    print(result)


cli = CLI(description="User management CLI", examples={"Create a user": "user create Alice"})

@cli.subcmd(examples={"Create with role": "user create Alice --role admin"})
def create(name: str, role: str = "user"):
    """Create a new user."""
    print(f"Created user '{name}' with role '{role}'")


@cli.subcmd(examples={"Delete by name": "user delete Alice"})
def delete(name: str, force: bool = False):
    """Delete a user."""
    flag = " --force" if force else ""
    print(f"Deleting user '{name}'{flag}")


if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1 and argv[1] in ("create", "delete"):
        cli.run()
    else:
        calc.run()
