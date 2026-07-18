from defcmd import cmd, Spec
from typing import Annotated


@cmd
def count_lines(content: Annotated[str, Spec(stdin=True)]):
    """Count the number of lines in piped input"""
    lines = content.split("\n")
    print(f"Lines: {len(lines)}")


if __name__ == "__main__":
    count_lines.run()
