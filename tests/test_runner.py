from defcmd.runner import cmd, CLI


class TestDescription:
    def test_cmd_description_override(self):
        @cmd(description="custom desc")
        def deploy(host: str, port: int = 8080):
            """docstring desc"""

        assert deploy.description == "custom desc"


    def test_cmd_description_falls_back_to_docstring(self):
        @cmd
        def deploy(host: str, port: int = 8080):
            """docstring desc"""

        assert deploy.description == "docstring desc"


    def test_cmd_description_defaults_to_none_when_no_docstring(self):
        @cmd
        def deploy(host: str, port: int = 8080):
            pass

        assert deploy.description is None


    def test_cli_subcmd_description_override(self):
        cli = CLI()

        @cli.subcmd(description="custom desc")
        def greet(name: str):
            """docstring desc"""

        assert cli.commands["greet"].description == "custom desc"


    def test_cli_subcmd_description_falls_back_to_docstring(self):
        cli = CLI()

        @cli.subcmd
        def greet(name: str):
            """docstring desc"""

        assert cli.commands["greet"].description == "docstring desc"


class TestHelp:
    def test_cmd_help_override(self):
        @cmd(help="short help")
        def deploy(host: str, port: int = 8080):
            """docstring desc"""

        assert deploy.help == "short help"


    def test_cmd_help_falls_back_to_description(self):
        @cmd(description="long desc")
        def deploy(host: str, port: int = 8080):
            """docstring desc"""

        assert deploy.help == "long desc"


    def test_cmd_help_falls_back_to_docstring(self):
        @cmd
        def deploy(host: str, port: int = 8080):
            """docstring desc"""

        assert deploy.help == "docstring desc"


    def test_cmd_help_defaults_to_none(self):
        @cmd
        def deploy(host: str, port: int = 8080):
            pass

        assert deploy.help is None


    def test_cli_subcmd_help_override(self):
        cli = CLI()

        @cli.subcmd(help="short help")
        def greet(name: str):
            """docstring desc"""

        assert cli.commands["greet"].help == "short help"


    def test_cli_subcmd_help_falls_back_to_description(self):
        cli = CLI()

        @cli.subcmd(description="long desc")
        def greet(name: str):
            """docstring desc"""

        assert cli.commands["greet"].help == "long desc"


    def test_cli_subcmd_help_falls_back_to_docstring(self):
        cli = CLI()

        @cli.subcmd
        def greet(name: str):
            """docstring desc"""

        assert cli.commands["greet"].help == "docstring desc"


class TestEpilog:
    def test_cmd_epilog_override(self):
        @cmd(epilog="see also: --help")
        def deploy(host: str):
            pass

        assert deploy.epilog == "see also: --help"


    def test_cmd_epilog_defaults_to_none(self):
        @cmd
        def deploy(host: str):
            pass

        assert deploy.epilog is None


    def test_cli_subcmd_epilog_override(self):
        cli = CLI()

        @cli.subcmd(epilog="see also: --help")
        def greet(name: str):
            pass

        assert cli.commands["greet"].epilog == "see also: --help"


    def test_cli_subcmd_epilog_defaults_to_none(self):
        cli = CLI()

        @cli.subcmd
        def greet(name: str):
            pass

        assert cli.commands["greet"].epilog is None


class TestAliases:
    def test_cli_subcmd_aliases_override(self):
        cli = CLI()

        @cli.subcmd(aliases=["ls", "list"])
        def greet(name: str):
            pass

        assert cli.commands["greet"].aliases == ["ls", "list"]


    def test_cli_subcmd_aliases_defaults_to_none(self):
        cli = CLI()

        @cli.subcmd
        def greet(name: str):
            pass

        assert cli.commands["greet"].aliases is None


class TestHidden:
    def test_cmd_hidden_defaults_to_false(self):
        @cmd
        def deploy(host: str):
            pass

        assert deploy.hidden is False


    def test_cmd_hidden_true(self):
        @cmd(hidden=True)
        def deploy(host: str):
            pass

        assert deploy.hidden is True


    def test_cli_subcmd_hidden_true(self):
        cli = CLI()

        @cli.subcmd(hidden=True)
        def greet(name: str):
            pass

        assert cli.commands["greet"].hidden is True


class TestVersion:
    def test_cmd_version_override(self):
        @cmd(version="1.0.0")
        def deploy(host: str):
            pass

        assert deploy.version == "1.0.0"


    def test_cmd_version_defaults_to_none(self):
        @cmd
        def deploy(host: str):
            pass

        assert deploy.version is None


    def test_cli_version_override(self):
        cli = CLI(version="2.0.0")
        assert cli.version == "2.0.0"
