import pytest
from defcmd import CLI



def test_dispatch_by_name():
    cli = CLI()
    calls = []

    @cli.subcmd
    def init(name: str):
        calls.append(("init", name))

    cli.run(["init", "test_project"])
    assert calls == [("init", "test_project")]



def test_dispatch_multiple_commands():
    cli = CLI()
    calls = []

    @cli.subcmd
    def init(name: str):
        calls.append(("init", name))

    @cli.subcmd
    def build(clean: bool = False):
        calls.append(("build", clean))

    cli.run(["build", "--clean"])
    assert calls == [("build", True)]



def test_unknown_subcommand_exists(monkeypatch):
    cli = CLI()

    @cli.subcmd
    def init(name: str):
        pass

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(SystemExit):
        cli.run(["unknown_command"])



def test_help_list_subcommands(capsys):
    cli = CLI(description="Test CLI")

    @cli.subcmd
    def init(name: str):
        """Initialize a project"""
        pass

    @cli.subcmd
    def build(clean: bool = False):
        """Build the project"""
        pass

    with pytest.raises(SystemExit):
        cli.run(["--help"])

    captured = capsys.readouterr()
    assert "Test CLI" in captured.out
    assert "init" in captured.out
    assert "build" in captured.out
    assert "Initialize a project" in captured.out
    assert "Build the project" in captured.out



def test_name_override():
    cli = CLI()

    @cli.subcmd(name="start")
    def init(name: str):
        """Initialize a project"""
        pass

    # The command should be registered under the name "start" instead of "init"
    assert "start" in cli.commands
    assert "init" not in cli.commands



def test_description_override():
    cli = CLI()

    @cli.subcmd(description="Custom description for init command")
    def init(name: str):
        """Initialize a project"""
        pass

    # The command's description should be overridden
    assert cli.commands["init"].description == "Custom description for init command"



def test_description_override_help(capsys):
    cli = CLI(description="Test CLI")

    @cli.subcmd(description="Custom description for init command")
    def init(name: str):
        """Initialize a project"""
        pass

    with pytest.raises(SystemExit):
        cli.run(["init", "--help"])

    captured = capsys.readouterr()
    assert "Custom description for init command" in captured.out

