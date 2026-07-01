from defcmd import CLI, Spec
from typing import Annotated


cli = CLI(description="Example CLI with subcommands")

@cli.subcmd
def echo(message: str, uppercase:Annotated[bool, Spec(short='u')] = False):
    """Echo a message back to the user, optionally in uppercase."""
    if uppercase:
        message = message.upper()
    print(message)


@cli.subcmd(name="greet", description="Greet a user")
def greet(name: str, times: int = 1, excited: bool = False):
    """Greet a user a specified number of times, optionally with excitement."""
    greeting = f"Hello, {name}!"
    if excited:
        greeting += "!!!"
    for _ in range(times):
        print(greeting)


@cli.subcmd(name="farewell", description="Bid farewell to a user")
def farewell(
    name: Annotated[str, Spec(help="The name of the user to bid farewell")],
    times: Annotated[int, Spec(short="t", help="Number of times to bid farewell", min=1)] = 1,
    emotional: Annotated[bool, Spec(short="e", help="Whether to add an emotional touch to the farewell")] = False
):
    """Bid farewell to a user a specified number of times."""
    farewell_message = f"Goodbye, {name}!"
    if emotional:
        farewell_message += " 😢"
    for _ in range(times):
        print(farewell_message)


if __name__ == "__main__":
    cli.run()
