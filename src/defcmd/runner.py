"""
TODO: Public API. @cmd decorator that turns a function into a runnable command.
"""

from __future__ import annotations

import sys
import argparse

from defcmd.argparser import build_parser
from defcmd.introspect import inspect_function_signature
from defcmd.interactive import is_interactive
from defcmd.widgets import prompt, SelectWidget

from typing import Callable, TypeAlias

ArgSubparsers: TypeAlias = argparse._SubParsersAction  # Type alias for subparsers in argparse

# Decorator to turn a function into a Cmd instance
def cmd(fn):
    """Use the function signature to create a command-line interface"""
    return Cmd(fn)

class Cmd:
    def __init__(self, fn):
        self.fn = fn
        self.params = inspect_function_signature(fn)
        self.description = fn.__doc__

    def run(self, argv=None):
        """Run the command with the provided arguments or prompt interactively if no arguments are given"""

        # If no arguments are provided, use the system command line arguments
        if argv is None:
            argv = sys.argv[1:] # Skip the script name and use the rest of the args

        # If no arguments are provided and we're in an interactive environment, run the interactive wizard
        if is_interactive(argv):
            return self.run_wizard()
        
        # Otherwise, run the command with the provided arguments

        # Build the argument parser based on the function's parameters and parse the provided arguments
        parser = build_parser(self.params, description=self.description)
        args = parser.parse_args(argv)

        # Extract the parsed arguments and call the function with them
        kwargs = {param.name: getattr(args, param.name) for param in self.params}
        return self.fn(**kwargs)

    def run_wizard(self):
        """Run an interactive wizard to prompt the user for each parameter"""
        kwargs = {}
        for param in self.params:
            kwargs[param.name] = prompt(param)
        return self.fn(**kwargs)
    
    def attach_to_parser(self, subparsers: ArgSubparsers, name: str):
        """Attach this command's parser to a provided parent command's subparsers, allowing for nested commands"""
        parser = subparsers.add_parser(name, description=self.description, help=self.description)
        build_parser(self.params, parser=parser)

class CLI:
    def __init__(self, description: str | None = None):
        self.description = description  # Optional description for the CLI, used in the help message
        self.commands = {}  # Dictionary to hold command names and their corresponding Cmd instances

    def subcmd(self, fn: Callable | None = None, *, name: str | None =None, description: str | None = None):
        """Decorator to register a function as a subcommand of the CLI"""

        def decorator(fn: Callable):
            cmd_name = name or fn.__name__      # Use the provided name or the function's name as the command name
            cmd = Cmd(fn)                       # Create a Cmd instance 
            # Set the description if provided (otherwise, it will default to the function's docstring)
            if description is not None:
                cmd.description = description
            self.commands[cmd_name] = cmd       # Store the command in the CLI's commands dictionary
            return fn

        if fn is not None:
            return decorator(fn)  # If a function is provided, apply the decorator immediately

        return decorator  # Otherwise, return the decorator for later use

    def group(self, name: str, description: str | None = None):
        """Creates a subcommand group, allowing for nested commands"""
        group_cli = CLI(description=description)  # Create a new CLI instance for the group
        self.commands[name] = group_cli           # Register the group as a command in the parent CLI
        return group_cli                          # Return the group CLI for further command registration

    def run(self, argv: list[str] | None = None):
        """Runs the CLI, parsing the command-line arguments and dispatching to the appropriate subcommand"""

        # If no arguments are provided, use the system command line arguments
        if argv is None:
            argv = sys.argv[1:]  # Skip the script name and use the rest of the args

        # If no arguments are provided and we're in an interactive environment, run the interactive wizard for the CLI
        # TODO: Implement a more sophisticated interactive mode that allows the user to select a command and then prompts for its parameters
        if is_interactive(argv):
            widget = SelectWidget(
                prompt="Select a command to run",
                options=list(self.commands.keys()),
                default=None,
            )
            cmdname = widget.value
            if cmdname in self.commands:
                return self.commands[cmdname].run([])
            print(f"Error: '{cmdname}' is not a valid command.")
            return

        # If no arguments are provided or the first argument is not a registered command, display the help message
        if not argv or argv[0] not in self.commands:
            parser = build_parser([], description=self.description)
            subparsers = parser.add_subparsers(required=True)
            for name, cmd in self.commands.items():
                cmd.attach_to_parser(subparsers, name)
            parser.parse_args(argv)  # handles --help, missing cmd, invalid cmd

        # If a valid command is provided, dispatch to the corresponding Cmd instance's run method with the remaining arguments
        cmdname, *rest = argv
        return self.commands[cmdname].run(rest) 

    def attach_to_parser(self, subparsers: ArgSubparsers, name: str):
        """Attach this CLI's parser to a provided parent command's subparsers, allowing for nested commands"""
        parser = subparsers.add_parser(name, description=self.description, help=self.description)
        inner = parser.add_subparsers(dest="__cmd", required=True)
        for subname, subcmd in self.commands.items():
            subcmd.attach_to_parser(inner, subname)
