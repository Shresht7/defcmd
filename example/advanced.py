from typing import Annotated
from defcmd.spec import Spec
from defcmd.runner import cmd

@cmd
def action(
    username: Annotated[str, Spec(help="user's display name")],
    email: Annotated[str, Spec(help="user's email address", prompt="How should we contact you?")],
    password: Annotated[str, Spec(help="user's password", prompt="password", secret=True)],
    ):
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")

if __name__ == "__main__":
    action.run()
