"""
Command execution and CLI composition.

This module provides the public API for building command-line applications from Python functions.

It defines the `@cmd` decorator for exposing a single function as a command,
the `Cmd` class for executing an individual command, and the `CLI` class for
composing multiple commands into a hierarchical command-line interface.

Commands can be executed from command-line arguments or, when appropriate, through an interactive prompting workflow.
"""

from __future__ import annotations

import sys
import argparse

from .argparser import build_parser
from .introspect import inspect_function_signature
from .interactive import is_interactive
from .widgets import prompt, SelectWidget

from typing import Callable, TypeAlias, overload, Any, Unpack, TypedDict

# CAUTION: argparse does not expose a public type for subparser collections
ArgSubparsers: TypeAlias = argparse._SubParsersAction  # Type alias for subparsers in argparse

Fn: TypeAlias = Callable[..., Any]  # Type alias for a callable function that takes any arguments and returns any value


class CmdOptions(TypedDict, total=False):
    """Keyword arguments accepted by @cmd(), @cli.subcmd(), and CLI()."""
    help: str | None
    description: str | None
    epilog: str | None
    aliases: list[str] | None
    prompt_optional: bool | None


# ---
# CMD
# ---

@overload
def cmd(fn: Fn, **kwargs: Unpack[CmdOptions]) -> Cmd: ...
@overload
def cmd(**kwargs: Unpack[CmdOptions]) -> Callable[[Fn], Cmd]: ...


def cmd(fn: Fn | None = None, **kwargs: Unpack[CmdOptions]) -> Cmd | Callable[[Fn], Cmd]:
    """Use the function signature to create a command-line interface"""

    # If a function is provided, create a Cmd instance immediately
    if fn is not None:
        return Cmd(fn, **kwargs)

    # Otherwise, return a decorator for later use
    def decorator(f: Fn) -> Cmd:
        return Cmd(f, **kwargs)    
    return decorator


class Cmd:
    """Represents a command-line command, wrapping a Python function and providing argument parsing and interactive prompting"""

    def __init__(self, fn: Fn, *, help: str | None = None, description: str | None = None, epilog: str | None = None, aliases: list[str] | None = None, prompt_optional: bool | None = True):
        self.fn = fn
        self.params = inspect_function_signature(fn)
        self.description = description or fn.__doc__
        self.help = help or self.description
        self.epilog = epilog
        self.aliases = aliases
        self.prompt_optional = prompt_optional


    # Allow the Cmd instance to be called like a function, forwarding arguments to the underlying function
    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


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
        parser = build_parser(self.params, description=self.description, epilog=self.epilog)
        args = parser.parse_args(argv)

        # Extract the parsed arguments and call the function with them
        kwargs = {param.name: getattr(args, param.name) for param in self.params}
        return self.fn(**kwargs)


    def run_wizard(self):
        """Run an interactive wizard to prompt the user for each parameter"""
        kwargs = {}
        for param in self.params:
            kwargs[param.name] = prompt(param, prompt_optional=bool(self.prompt_optional))
        return self.fn(**kwargs)


    def attach_to_parser(self, subparsers: ArgSubparsers, name: str):
        """Attach this command's parser to a provided parent command's subparsers, allowing for nested commands"""
        parser = subparsers.add_parser(name, description=self.description, help=self.help, epilog=self.epilog, aliases=self.aliases or [])
        build_parser(self.params, parser=parser)


# ---
# CLI
# ---

class CLI:
    def __init__(self, **kwargs: Unpack[CmdOptions]):
        self.description = kwargs.get("description")
        self.help = kwargs.get("help") or self.description
        self.commands = {}


    @overload
    def subcmd(self, fn: Fn, *, name: str | None = None, **kwargs: Unpack[CmdOptions]) -> Fn: ...
    @overload
    def subcmd(self, *, name: str | None = None, **kwargs: Unpack[CmdOptions]) -> Callable[[Fn], Fn]: ...

    def subcmd(self, fn=None, *, name=None, **kwargs: Unpack[CmdOptions]):
        """Decorator to register a function as a subcommand of the CLI"""

        def decorator(fn: Fn) -> Fn:
            cmd_name = name or fn.__name__
            cmd = Cmd(fn, **kwargs)
            self.commands[cmd_name] = cmd
            return fn

        if fn is not None:
            return decorator(fn)

        return decorator


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
        parser = subparsers.add_parser(name, description=self.description, help=self.help)
        inner = parser.add_subparsers(dest="__cmd", required=True)
        for subname, subcmd in self.commands.items():
            subcmd.attach_to_parser(inner, subname)
