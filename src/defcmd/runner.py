"""
TODO: Public API. @cmd decorator that turns a function into a runnable command.
"""

from __future__ import annotations

import sys

from defcmd.argparser import build_parser
from defcmd.introspect import Parameter, inspect_function_signature
from defcmd.interactive import is_interactive
from defcmd.prompt import prompt_for_param

from typing import Callable

from defcmd.spec import Spec

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
            kwargs[param.name] = prompt_for_param(param)
        return self.fn(**kwargs)

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

    def run(self, argv: list[str] | None = None):
        """Runs the CLI, parsing the command-line arguments and dispatching to the appropriate subcommand"""

        # If no arguments are provided, use the system command line arguments
        if argv is None:
            argv = sys.argv[1:]  # Skip the script name and use the rest of the args

        # Create a top-level parser for the CLI itself
        parser = build_parser([], description=self.description)

        # Create a subparser for each registered command
        subparsers = parser.add_subparsers(dest="command", required=True) 
        for cmd_name, cmd in self.commands.items():
            subparser = subparsers.add_parser(cmd_name, description=cmd.description, help=cmd.description)
            build_parser(cmd.params, parser=subparser)

        # If no arguments are provided and we're in an interactive environment, run the interactive wizard for the CLI
        # TODO: Implement a more sophisticated interactive mode that allows the user to select a command and then prompts for its parameters
        if is_interactive(argv):
            print("Available commands:")
            for cmd_name in self.commands:
                print(f"  {cmd_name}")
            cmd_name = input("Enter a command: ").strip()
            if cmd_name not in self.commands:
                print(f"Error: '{cmd_name}' is not a valid command.")
                return
            cmd = self.commands[cmd_name]
            return cmd.run_wizard()
        
        # Parse the command-line arguments
        args = parser.parse_args(argv)

        # Dispatch to the appropriate subcommand based on the parsed command name
        cmd_name = args.command
        cmd = self.commands[cmd_name]
        cmd_args = {param.name: getattr(args, param.name) for param in cmd.params}
        return cmd.fn(**cmd_args)
