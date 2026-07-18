from __future__ import annotations

import io
import pytest
from typing import Annotated

from defcmd.runner import cmd
from defcmd.spec import Spec


def test_stdin_str_param(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("hello from stdin"))

    calls = []
    @cmd
    def greet(data: Annotated[str, Spec(stdin=True)]):
        calls.append(data)

    greet.run([])
    assert calls == ["hello from stdin"]


def test_stdin_int_param(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("42"))

    calls = []
    @cmd
    def double(value: Annotated[int, Spec(stdin=True)]):
        calls.append(value)

    double.run([])
    assert calls == [42]


def test_stdin_list_param(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("a\nb\nc\n"))

    calls = []
    @cmd
    def collect(items: Annotated[list[str], Spec(stdin=True)]):
        calls.append(items)

    collect.run([])
    assert calls == [["a", "b", "c"]]


def test_stdin_list_with_delimiter(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("a,b,c"))

    calls = []
    @cmd
    def collect(items: Annotated[list[str], Spec(stdin=True, delimiter=",")]):
        calls.append(items)

    collect.run([])
    assert calls == [["a", "b", "c"]]


def test_stdin_list_int_conversion(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("1\n2\n3\n"))

    calls = []
    @cmd
    def collect(items: Annotated[list[int], Spec(stdin=True)]):
        calls.append(items)

    collect.run([])
    assert calls == [[1, 2, 3]]


def test_stdin_empty_uses_default(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    calls = []
    @cmd
    def collect(items: Annotated[list[str], Spec(stdin=True)] = []):
        calls.append(items)

    collect.run([])
    assert calls == [[]]


def test_stdin_cli_override_takes_priority(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("should not be used"))

    calls = []
    @cmd
    def greet(data: Annotated[str, Spec(stdin=True)]):
        calls.append(data)

    greet.run(["from_cli"])
    assert calls == ["from_cli"]
