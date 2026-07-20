from __future__ import annotations

import io
from typing import Annotated

from defcmd.runner import cmd
from defcmd.spec import Spec


class TestStdinScalar:

    def test_stdin_str_param(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("hello from stdin"))

        calls = []
        @cmd
        def greet(data: Annotated[str, Spec(stdin=True)]):
            calls.append(data)

        greet.run([])
        assert calls == ["hello from stdin"]


    def test_stdin_int_param(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("42"))

        calls = []
        @cmd
        def double(value: Annotated[int, Spec(stdin=True)]):
            calls.append(value)

        double.run([])
        assert calls == [42]


    def test_stdin_bool_param(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("true"))

        calls = []
        @cmd
        def flag(value: Annotated[bool, Spec(stdin=True)]):
            calls.append(value)

        flag.run([])
        assert calls == [True]


    def test_stdin_bool_param_no_value(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("no"))

        calls = []
        @cmd
        def flag(value: Annotated[bool, Spec(stdin=True)]):
            calls.append(value)

        flag.run([])
        assert calls == [False]


class TestStdinList:

    def test_stdin_list_param(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("a\nb\nc\n"))

        calls = []
        @cmd
        def collect(items: Annotated[list[str], Spec(stdin=True)]):
            calls.append(items)

        collect.run([])
        assert calls == [["a", "b", "c"]]


    def test_stdin_list_with_delimiter(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("a,b,c"))

        calls = []
        @cmd
        def collect(items: Annotated[list[str], Spec(stdin=True, delimiter=",")]):
            calls.append(items)

        collect.run([])
        assert calls == [["a", "b", "c"]]


    def test_stdin_list_int_conversion(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("1\n2\n3\n"))

        calls = []
        @cmd
        def collect(items: Annotated[list[int], Spec(stdin=True)]):
            calls.append(items)

        collect.run([])
        assert calls == [[1, 2, 3]]


    def test_stdin_empty_uses_default(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO(""))

        calls = []
        @cmd
        def collect(items: Annotated[list[str], Spec(stdin=True)] = []):
            calls.append(items)

        collect.run([])
        assert calls == [[]]


class TestStdinPriority:

    def test_stdin_cli_override_takes_priority(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("should not be used"))

        calls = []
        @cmd
        def greet(data: Annotated[str, Spec(stdin=True)]):
            calls.append(data)

        greet.run(["from_cli"])
        assert calls == ["from_cli"]


    def test_stdin_multiple_params(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("from_stdin"))

        calls = []
        @cmd
        def process(data: Annotated[str, Spec(stdin=True)], items: Annotated[list[str], Spec(stdin=True)] = []):
            calls.append((data, items))

        process.run(["from_cli"])
        assert calls == [("from_cli", ["from_stdin"])]
