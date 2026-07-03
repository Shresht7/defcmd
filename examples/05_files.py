"""
Example demonstrating path arguments with `pathlib.Path`, Spec validation, and glob patterns
"""

from pathlib import Path
from glob import glob

from defcmd import CLI, Spec
from typing import Annotated


cli = CLI(description="File operations demo")

@cli.subcmd
def show(
    info: Annotated[Path, Spec(path_exists=True, path_type="file",help="File to display")],
):
    """Display metadata about a file"""
    print(f"Name: {info.name}")
    print(f"Size: {info.stat().st_size} bytes")
    print(f"Absolute: {info}")


@cli.subcmd
def find(
    pattern: Annotated[str, Spec(
        help="Glob pattern (e.g. '**/*.py')"
    )],
    
    root: Annotated[Path, Spec(
        path_type="dir",
        path_exists=True,
        help="Root directory"
    )] = Path("."),
):
    """Find files matching a glob pattern under a root directory"""
    full_pattern = str(root / pattern)
    for path in sorted(glob(full_pattern, recursive=True)):
        print(path)


@cli.subcmd
def validate(
    target: Annotated[Path, Spec(path_exists=True, path_type="file", help="File to validate")],
):
    """Validate that a file exists and show its resolved path"""
    print(f"OK: {target}")


if __name__ == "__main__":
    cli.run()
