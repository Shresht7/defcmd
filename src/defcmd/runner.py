"""
TODO: Public API. @cmd decorator that turns a function into a runnable command.
"""

from __future__ import annotations

import sys

from defcmd.argparser import build_parser
from defcmd.introspect import inspect_function_signature
from defcmd.interactive import is_interactive
from defcmd.prompt import prompt_for_param

# Decorator to turn a function into a Cmd instance
def cmd(fn):
    """Use the function signature to create a command-line interface"""
    return Cmd(fn)

class Cmd:
    def __init__(self, fn):
        self.fn = fn
        self.params = inspect_function_signature(fn)

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
        parser = build_parser(self.params)
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
