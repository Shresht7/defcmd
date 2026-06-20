"""
This module contains the logic for building an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature.
It defines a single function, `build_parser`, which takes a list of `Parameter` objects
and returns an `ArgumentParser` that can be used to parse command-line arguments corresponding to those parameters.
"""

from __future__ import annotations

import argparse
from .introspect import Parameter

def build_parser(params: list[Parameter]) -> argparse.ArgumentParser:
    """Build an `argparse.ArgumentParser` based on the list of `Parameter` objects extracted from a function signature"""
    parser = argparse.ArgumentParser()

    for param in params:
        if param.required:
            parser.add_argument(param.name, type=param.annotation)

    return parser
