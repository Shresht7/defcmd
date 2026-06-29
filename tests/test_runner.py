from defcmd.runner import cmd

def test_full_argv_runs_without_prompting(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080, verbose: bool = False):
        calls.append((host, port, verbose))

    monkeypatch.setattr("builtins.input", lambda *_: (_ for _ in ()).throw(AssertionError("should not prompt")))

    deploy.run(["localhost", "--port", "1234", "--verbose"])
    assert calls == [("localhost", 1234, True)]

def test_run_with_default_argv(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080):
        calls.append((host, port))

    monkeypatch.setattr("sys.argv", ["script.py", "localhost", "--port", "9090"])
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    deploy.run()
    assert calls == [("localhost", 9090)]


def test_empty_argv_in_real_terminal_runs_wizard(monkeypatch):
    calls = []

    @cmd
    def deploy(host: str, port: int = 8080, verbose: bool = False):
        calls.append((host, port, verbose))

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    prompted = iter(["wizardhost", 9090, True])
    monkeypatch.setattr("defcmd.runner.prompt", lambda _param: next(prompted))

    deploy.run([])
    assert calls == [("wizardhost", 9090, True)]
