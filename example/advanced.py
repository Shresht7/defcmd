from typing import Annotated
from defcmd.spec import Spec
from defcmd.runner import cmd

@cmd
def deploy(
    host: Annotated[str, Spec(help="target hostname", secret=True)]
    ):
    print(f"Deploying to {host}...")

if __name__ == "__main__":
    deploy.run()
