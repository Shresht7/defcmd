from defcmd import CLI, Spec
from typing import Annotated

# Instantiate a CLI object
cli = CLI(description="A CLI with nested subcommands")

# Regular command registration works as is
@cli.subcmd
def init(name: str):
    """Initialize a new project with the given name"""
    print(f"Initializing project: {name}")


# Create a subcommand group for 'database' related commands
db = cli.group("database", description="Database management commands")

# Register subcommands under the 'database' group

@db.subcmd
def migrate(version: Annotated[int, Spec(short='v')]):
    """Migrate the database to the specified version"""
    print(f"Migrating database to version: {version}")

@db.subcmd
def seed(data: str):
    """Seed the database with the provided data"""
    print(f"Seeding database with data: {data}")


# Run the CLI with the provided command-line arguments
if __name__ == "__main__":
    cli.run()


# $ python example/nested_subcommands.py --help
# $ python example/nested_subcommands.py init --name MyProject

# $ python example/nested_subcommands.py database --help
# $ python example/nested_subcommands.py database migrate --version 2
