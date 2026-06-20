from defcmd.runner import cmd

def test_full_argv_runs_without_prompting(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080, verbose: bool = False):
        calls.append((host, port, verbose))

    monkeypatch.setattr("builtins.input", lambda *_: (_ for _ in ()).throw(AssertionError("should not prompt")))

    deploy.run(["localhost", "--port", "1234", "--verbose"])
    assert calls == [("localhost", 1234, True)]

# ? Figure out a way to unit test the interactive prompting wizard.
