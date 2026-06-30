from defcmd import cmd, Spec
from typing import Annotated, Literal

@cmd
def action(
        payload: Annotated[Literal["json", "xml", "csv", "html"], Spec(help="The payload to send", prompt="Payload")],
        token: Annotated[str, Spec(short="t", help="The authentication token", prompt="Enter your token", secret=True)],
        host: Annotated[str, Spec(help="The host to connect to")] = "localhost",
        port: Annotated[int, Spec(short='p', help="The port to connect to")] = 8080,
        verbose: Annotated[bool, Spec(short='v', help="Enable verbose output")] = False
    ):
    print(f"Host: {host}")
    print(f"Port: {port}")
    if verbose:
        print(f"Token: {'*' * len(token)}")
    print(f"Payload: {payload}")

if __name__ == "__main__":
    action.run()
