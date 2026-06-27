# `defcmd`

Turn any Python function signature into a command-line script.

> "I thought _Python_ was supposed to be ***the scripting language!*** why do I have to write 100 lines of boilerplate with `argparse` just to make a simple script?!" 
> <br> — You, probably

```python
from defcmd import cmd

@cmd
def greet(name: str, times: int = 1, excited: bool = False):
    """Greet a person a specified number of times, optionally with excitement."""
    greeting = f"Hello, {name}!"
    if excited:
        greeting = greeting.upper() + "!!!"
    for _ in range(times):
        print(greeting)

if __name__ == "__main__":
    greet.run()

```

This will create a command-line interface that allows you to call the `greet` function with the appropriate arguments. For example:

```bash
python greet.py Alice --times 3 --excited
```
`defcmd` scripts support interactive mode as well, allowing you to call the function without providing any arguments upfront. You can simply run the script and it will prompt you for the inputs:

```bash
$ python greet.py
Name: Alice
Times [1]:   # Leave blank for default value
Excited [y/N]: y
HELLO, ALICE!!!
```
> [!TIP]
> Use `--help` for full usage information as provided by `argparse`.

Zero external dependencies. Built on `argparse` and `inspect` from the standard library.

Takes inspiration from **PowerShell** (of all places!) and the [`fncmd`](https://github.com/yuhr/fncmd) crate that I stumbled across when trying something similar in Rust. 

The goal is to make it **easy to write small scripts** that are **usable from the command line** without having to write a lot of boilerplate.

> [!NOTE]
> `defcmd` is **not** supposed to be a full-featured CLI framework like `click` or `typer`. It is intentionally minimal, and is designed for **small scripts** where you want to avoid boilerplate and just get the **job done**.

---

## 📖 Documentation

### Defining a command

Any plain function becomes a CLI when decorated with `@cmd`:

```python
from defcmd import cmd

@cmd
def greet(name: str, times: int = 1, excited: bool = False):
    """Greet a person a specified number of times, optionally with excitement."""
    # ... Your Logic Here ...

if __name__ == "__main__":
    greet.run()
```

`defcmd` derives everything (argument names, types, defaults, required-ness) directly from the function signature. There's no separate schema to keep in sync.

### Required vs. optional parameters

A parameter with **no default value** is required and becomes a **positional argument**:

```python
def greet(name: str):
    ...
```
```bash
python greet.py Alice
```

A parameter **with a default value** becomes an **optional `--flag`**:

```python
def greet(name: str, times: int = 1):
    ...
```
```bash
python greet.py Alice --times 3
```

### Boolean flags

`bool` parameters are always flags, never positionals, even if required. They support both the on and off form:

```python
def greet(name: str, excited: bool = False):
    ...
```
```bash
python greet.py Alice --excited
python greet.py Alice --no-excited
```

### Choices with `Literal`

A `typing.Literal[...]` annotation restricts the value to a fixed set of choices, enforced by argparse:

```python
from typing import Literal

def deploy(env: Literal["dev", "staging", "prod"] = "dev"):
    ...
```
```bash
python deploy.py --env staging
python deploy.py --env nope   # error: invalid choice
```

### Interactive mode

Run the script with **no arguments at all**, from a real terminal, and `defcmd` walks through every parameter, prompting for each one in order:

```bash
$ python greet.py
Name: Alice
Times [1]:        # press Enter to accept the default
Excited [y/N]: y
HELLO, ALICE!!!
```

- Required parameters will keep re-prompting until you enter something; blank input isn't accepted.
- Optional parameters show their default in brackets; pressing Enter accepts it.
- Boolean parameters accept `y`/`n`, `yes`/`no`, `true`/`false`, or `1`/`0`.
- `Literal` parameters list the valid choices and accept either the exact value or its number.

When using the advanced `Spec` annotations:
- Parameters with `Spec(prompt=...)` can override the default prompt text.
- Parameters with `Spec(secret=True)` hide the input (for passwords, tokens, etc.).
- Parameters with `Spec(help=...)` can override the default help text shown in `--help`.
- Parameters with validation constraints (`min`, `max`, `pattern`) will re-prompt until the value satisfies the constraint.

Interactive mode only triggers when **both** of these are true: no arguments were passed, and stdin is a real terminal (not piped or redirected). Running a script with no args in a non-interactive context (cron, CI, piped input) just errors normally instead of hanging waiting for input.

### Help text

The function's docstring is shown as the description in `--help`:

```python
def deploy(host: str):
    """Deploy the application to a target host."""
    ...
```
```bash
$ python deploy.py --help
usage: deploy.py [-h] host

Deploy the application to a target host.

positional arguments:
  host
```

Use `Annotated[..., Spec(...)]` to add per-parameter metadata — see below.

### Advanced Parameter Specification

The `Spec` annotations allow you to attach additional metadata to the cli parameters:

```python
from typing import Annotated
from defcmd import cmd
from defcmd.spec import Spec

@cmd
def action(
        payload: Annotated[str, Spec(help="The payload to send", prompt="Payload")],
        token: Annotated[str, Spec(short="t", help="The authentication token", prompt="Enter your token", secret=True)],
        host: Annotated[str, Spec(help="The host to connect to")] = "localhost",
        port: Annotated[int, Spec(short='p', min=1, max=65535, help="The port to connect to")] = 8080,
        verbose: Annotated[bool, Spec(short='v', help="Enable verbose output")] = False
    ):
    # ... Your Logic Here ...

if __name__ == "__main__":
    action.run()
```

```sh
$ python action.py -p 8080 -v
Payload: Hello World
Enter your token: ********
# ... Your Logic Here ...
```

#### Specification Options

| Spec       | Description                                              | Overrides                |
| ---------- | -------------------------------------------------------- | ------------------------ |
| `short`    | Short flag for the parameter (e.g., `-p`).               |                          |
| `help`     | Help text for the parameter, shown in `--help`.          | The default help message |
| `prompt`   | Custom prompt text for interactive mode.                 | The default prompt text  |
| `secret`   | If `True`, input is hidden in interactive mode.          |                          |
| `min`      | Minimum numeric value (inclusive).                       |                          |
| `max`      | Maximum numeric value (inclusive).                       |                          |
| `pattern`  | A regex pattern the value must match (uses `fullmatch`). |                          |
| `validate` | A custom validation function for the parameter.          |                          |

### Subcommands

Multiple commands can be grouped together using `CLI`:

```python
from defcmd import CLI

cli = CLI(description="Project management tool")

@cli.subcmd
def init(name: str):
    """Initialize a new project"""
    print(f"Project '{name}' created")

@cli.subcmd(name="build-all")
def build(clean: bool = False):
    """Build the project"""
    print("Building... (clean={clean})")

@cli.subcmd(description="Deploy to production (overrides docstring)")
def deploy(env: str = "prod"):
    """Deploy the project"""
    print(f"Deploying to {env}")

if __name__ == "__main__":
    cli.run()
```

```bash
$ python project.py --help
usage: project.py [-h] {init,build-all,deploy} ...

Project management tool

positional arguments:
  {init,build-all,deploy}
    init                 Initialize a new project
    build-all            Build the project
    deploy               Deploy to production (overrides docstring)

$ python project.py init myapp
Project 'myapp' created

$ python project.py deploy --env staging
Deploying to staging
```

Run with no arguments in a terminal to pick a command interactively:

```bash
$ python project.py
Available commands:
  init
  build-all
  deploy
Enter a command: init
Name: myapp
Project 'myapp' created
```

The `@cli.subcmd` decorator accepts:
- `name` — override the subcommand name (defaults to the function name).
- `description` — override the help text (defaults to the function docstring).

---

### What's not supported (yet)

- `*args` and `**kwargs` in the decorated function's signature raises an error at decoration time.

---

## 🚧 Development

This is a [`uv`](https://docs.astral.sh/uv/) project. `uv` manages the virtual environment, dependencies, and the lockfile (`uv.lock`).

### 💽 Setup

Clone the repo and sync dependencies (this creates a `.venv` and installs everything needed, including dev dependencies like `pytest`):

```sh
git clone https://github.com/Shresht7/defcmd.git
cd defcmd
uv sync
```

### 🏗️ Project structure

```
./
├── example/
│   ├── script.py               # Basic Example
│   └── advanced.py             # Advanced Spec Example
├── src/
│   └── defcmd/
│       ├── __init__.py         # Package Init
│       ├── argparser.py        # Argument Parser
│       ├── convert.py          # Type Conversion & Validation
│       ├── interactive.py      # Interactive Prompting Wizard
│       ├── introspect.py       # Function Signature Introspection
│       ├── prompt.py           # Prompt Utilities
│       ├── runner.py           # Command & CLI Runner
│       └── spec.py             # Spec Annotation
├── tests/
│   ├── test_argparser.py
│   ├── test_convert.py
│   ├── test_interactive.py
│   ├── test_introspect.py
│   ├── test_prompt.py
│   ├── test_runner.py
│   └── test_subcommands.py
├── .gitignore
├── .python-version
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

### 🧪 Testing

```sh
uv run pytest -v
```

The `example/` directory contains small manual scripts for trying behavior in a real terminal. `example/script.py` shows the basic API, while `example/advanced.py` shows `Annotated[..., Spec(...)]` metadata such as help text, custom prompts, secret input, and short flags. These examples are not part of the test suite, but they are useful for manually trying interactive behavior in a real tty.

```sh
uv run python example/script.py
```

### ☑️ TODO / Ideas 💡

- [ ] Write proper module documentation
- [ ] With `subcmd` done, add support for nested subcommands (like `git remote add`).

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
