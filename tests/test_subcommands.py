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



def test_subcommand_with_no_arguments():
    cli = CLI()
    calls = []

    @cli.subcmd
    def status():
        calls.append("status called")

    cli.run(["status"])
    assert calls == ["status called"]



def test_per_subcommand_help(capsys):
    cli = CLI(description="Test CLI")

    @cli.subcmd
    def init(name: str):
        """Initialize a project"""
        pass

    with pytest.raises(SystemExit):
        cli.run(["init", "--help"])

    captured = capsys.readouterr()
    assert "Initialize a project" in captured.out



def test_group_dispatch():
    cli = CLI()
    calls = []

    db = cli.group("db", description="Database commands")

    @db.subcmd
    def migrate(message: str):
        calls.append(("migrate", message))

    cli.run(["db", "migrate", "create_table"])
    assert calls == [("migrate", "create_table")]


def test_group_dispatch_with_flags():
    cli = CLI()
    calls = []

    db = cli.group("db")

    @db.subcmd
    def seed(count: int = 10):
        calls.append(("seed", count))

    cli.run(["db", "seed", "--count", "50"])
    assert calls == [("seed", 50)]


def test_group_help_shows_nested_commands(capsys):
    cli = CLI(description="Root CLI")

    db = cli.group("db", description="Database commands")

    @db.subcmd
    def migrate(message: str):
        """Run database migrations"""
        pass

    with pytest.raises(SystemExit):
        cli.run(["db", "--help"])

    captured = capsys.readouterr()
    assert "Database commands" in captured.out
    assert "migrate" in captured.out
    assert "Run database migrations" in captured.out


def test_top_level_help_shows_groups(capsys):
    cli = CLI(description="Root CLI")

    @cli.subcmd
    def init(name: str):
        """Init a project"""
        pass

    db = cli.group("db", description="Database commands")

    @db.subcmd
    def migrate(message: str):
        """Run migrations"""
        pass

    with pytest.raises(SystemExit):
        cli.run(["--help"])

    captured = capsys.readouterr()
    assert "Root CLI" in captured.out
    assert "init" in captured.out
    assert "db" in captured.out
    assert "Database commands" in captured.out


def test_deeply_nested_subcommands(monkeypatch):
    cli = CLI()
    calls = []

    container = cli.group("container", description="Manage containers")
    logs = container.group("logs", description="View container logs")

    @logs.subcmd
    def show(name: str = "myapp"):
        calls.append(("show", name))

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    cli.run(["container", "logs", "show", "--name", "nginx"])
    assert calls == [("show", "nginx")]


def test_unknown_nested_command(monkeypatch):
    cli = CLI()
    db = cli.group("db")

    @db.subcmd
    def seed(count: int = 10):
        pass

    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(SystemExit):
        cli.run(["db", "unknown"])


def test_cli_run_with_default_argv(monkeypatch):
    cli = CLI()
    calls = []

    @cli.subcmd
    def status():
        calls.append("status called")

    monkeypatch.setattr("sys.argv", ["script.py", "status"])
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    cli.run()
    assert calls == ["status called"]


def test_group_description():
    cli = CLI()
    db = cli.group("db", description="Database commands")
    assert cli.commands["db"].description == "Database commands"


def test_group_subcmd_with_no_params():
    cli = CLI()
    calls = []

    db = cli.group("db")

    @db.subcmd
    def status():
        calls.append("status called")

    cli.run(["db", "status"])
    assert calls == ["status called"]


def test_group_in_group_help(capsys):
    cli = CLI(description="Root")
    container = cli.group("container")
    logs = container.group("logs", description="View container logs")

    @logs.subcmd
    def show():
        """Show container logs"""
        pass

    with pytest.raises(SystemExit):
        cli.run(["container", "logs", "--help"])

    captured = capsys.readouterr()
    assert "View container logs" in captured.out
    assert "show" in captured.out
    assert "Show container logs" in captured.out

