from __future__ import annotations

from pathlib import Path

from .introspect import Parameter
from .spec import Spec

import re
from typing import get_args, get_origin, Literal

VALID_BOOL_TRUE = frozenset({"true", "yes", "y", "1", "on"})
VALID_BOOL_FALSE = frozenset({"false", "no", "n", "0", "off"})

class ValidationError(ValueError):
    """Raised when a value fails validation against a Spec constraint"""
    pass

def parse_bool(raw: str) -> bool:
    """Parse a string into a boolean value, accepting various representations of true and false."""

    raw_lower = raw.lower()
    if raw_lower in VALID_BOOL_TRUE:
        return True
    elif raw_lower in VALID_BOOL_FALSE:
        return False
    else:
        raise ValueError(f"please enter a valid boolean (true/false, yes/no, y/n, 1/0, on/off) value, got: {raw}")

def convert_value(param: Parameter, raw: str):
    """Convert a raw string according to the parameter's type annotation"""

    annotation = param.annotation

    # Handle boolean conversion
    if annotation is bool:
        return parse_bool(raw)
    
    # Literal values remain as-is; type matching is done in parse_value()
    if get_origin(annotation) is Literal:
        return raw

    # Handle Path type
    if annotation is Path:
        p = Path(raw)
        if param.spec is None or param.spec.path_resolve:
            p = p.expanduser().resolve()
        return p

    # Handle common types    
    if isinstance(annotation, type) and annotation is not str:
        return annotation(raw)
    
    return raw  # Default case: return the raw string if no conversion is needed

def validate_value(param: Parameter, value):
    """Check Spec constraints against the convert value and raise ValidationError if any constraint is violated"""

    spec = param.spec

    # No spec to validate against
    if spec is None:
        return  

    # numeric bounds
    if spec.min is not None or spec.max is not None:
        if not isinstance(value, (int, float)):
            raise ValidationError(f"Value for parameter '{param.name}' must be a number to apply min/max constraints, got: {value}, {type(value).__name__}")
        if spec.min is not None and value < spec.min:
            raise ValidationError(f"must be at least {spec.min}, got: {value}")
        if spec.max is not None and value > spec.max:
            raise ValidationError(f"must be at most {spec.max}, got: {value}")

    # regex pattern
    if spec.pattern is not None:
        if not isinstance(value, str):
            raise ValidationError(f"Value for parameter '{param.name}' must be a string to apply pattern constraints, got: {value}, {type(value).__name__}")
        if not re.fullmatch(spec.pattern, value):
            raise ValidationError(f"must match pattern '{spec.pattern}', got: {value}")

    # custom validation function
    if spec.validate is not None:
        try:
            spec.validate(value)
        except Exception as e:
            raise ValidationError(f"custom validation failed: {e}")

    # Path validation
    if isinstance(value, Path):
        if spec.path_exists and not value.exists():
            raise ValidationError(f"path '{value}' does not exist")
        if spec.path_type is not None and value.exists():
            if spec.path_type == "file" and not value.is_file():
                raise ValidationError(f"path '{value}' is not a file")
            if spec.path_type == "dir" and not value.is_dir():
                raise ValidationError(f"path '{value}' is not a directory")

def parse_value(param: Parameter, raw: str):
    """Convert and validate a raw string value according to the parameter's type annotation and Spec constraints"""
    
    try:
        value = convert_value(param, raw)
    except ValueError as e:
        raise ValidationError(str(e))

    validate_value(param, value)

    # Literal choices check
    origin = get_origin(param.annotation)
    if origin is Literal:
        choices = get_args(param.annotation)
        if value not in choices:
            for c in choices:
                if str(c) == raw:
                    return c
            raise ValidationError(f"invalid choice: {value}. (choose from {', '.join(map(str, choices))})")

    return value
