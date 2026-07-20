import pytest

from defcmd.runner import cmd, CLI
from defcmd.terminal import strip_ansi


class TestCmdExamples:
    def test_cmd_examples_in_help(self, capsys):
        @cmd(examples={"Say hello to Alice": "greet Alice"})
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "examples:" in out
        assert "greet Alice        # Say hello to Alice" in out


    def test_cmd_examples_with_epilog(self, capsys):
        @cmd(
            examples={"Say hello to Alice": "greet Alice"},
            epilog="See the docs for more info.",
        )
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "examples:" in out
        assert "greet Alice        # Say hello to Alice" in out
        assert "See the docs for more info." in out


    def test_cmd_examples_none_omits_block(self, capsys):
        @cmd
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "examples:" not in out


    def test_cmd_examples_flag_suppressed(self, capsys):
        @cmd(examples={"Say hello to Alice": "greet Alice"}, add_examples_flag=False)
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--examples" not in out
        assert "examples:" in out
        assert "greet Alice        # Say hello to Alice" in out


    def test_cmd_examples_flag_default(self, capsys):
        @cmd(examples={"Say hello to Alice": "greet Alice"})
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            greet.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--examples" in out


class TestCLIExamples:
    def test_cli_top_level_examples_in_help(self, capsys):
        cli = CLI(examples={"Say hello": "greet Alice"})

        @cli.subcmd
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "examples:" in out
        assert "greet Alice        # Say hello" in out


    def test_cli_subcommand_examples_in_help(self, capsys):
        cli = CLI()

        @cli.subcmd(examples={"With feeling": "greet Alice"})
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["greet", "--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "examples:" in out
        assert "greet Alice        # With feeling" in out


    def test_cli_top_level_examples_flag_suppressed(self, capsys):
        cli = CLI(examples={"Say hello": "greet Alice"}, add_examples_flag=False)

        @cli.subcmd
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--examples" not in out
        assert "examples:" in out


    def test_cli_subcommand_examples_flag_suppressed(self, capsys):
        cli = CLI()

        @cli.subcmd(examples={"With feeling": "greet Alice"}, add_examples_flag=False)
        def greet(name: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["greet", "--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--examples" not in out
        assert "examples:" in out
        assert "greet Alice        # With feeling" in out


class TestGroupExamples:
    def test_cli_group_examples_in_help(self, capsys):
        cli = CLI()

        db = cli.group("db", examples={"Run migration": "cli db migrate --msg init"})

        @db.subcmd
        def migrate(msg: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["db", "--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--examples" in out
        assert "examples:" in out
        assert "cli db migrate --msg init" in out


    def test_cli_group_examples_flag_suppressed(self, capsys):
        cli = CLI()

        db = cli.group("db", examples={"Run migration": "cli db migrate --msg init"}, add_examples_flag=False)

        @db.subcmd
        def migrate(msg: str):
            pass

        with pytest.raises(SystemExit):
            cli.run(["db", "--help"])
        out = strip_ansi(capsys.readouterr().out)
        assert "--examples" not in out
        assert "examples:" in out
