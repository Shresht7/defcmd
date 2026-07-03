# `defcmd`

Turn any Python function signature into a command-line script.

> “I thought _Python_ was supposed to be ***the scripting language!*** why do I have to write 100 lines of boilerplate with `argparse` just to make a simple script?!”
> <br> — Me, _before writing 2000 lines of "minimal" cli framework_

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
> `defcmd` is **not** supposed to be a full-featured CLI framework like `click` or `typer`. It is intentionally minimal, and is designed for **small scripts** where you want to avoid boilerplate and just get the **job done**. At least, that was the goal when I began; I may have gotten a bit carried away.

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

#### `@cmd` parameters

| Parameter           | Type                     | Default                      | Description                                                 |
| ------------------- | ------------------------ | ---------------------------- | ----------------------------------------------------------- |
| `description`       | `str \| None`            | `fn.__doc__`                 | Override the help description for `--help`.                 |
| `help`              | `str \| None`            | `description` → `fn.__doc__` | Short help text for subcommand listings.                    |
| `examples`          | `dict[str, str] \| None` | `None`                       | Usage examples shown in `--help` via `--examples` flag.     |
| `epilog`            | `str \| None`            | `None`                       | Text displayed after argument help in `--help`.             |
| `version`           | `str \| None`            | `None`                       | Adds `--version` / `-v` flag that prints and exits.         |
| `hidden`            | `bool`                   | `False`                      | Exclude from interactive command selection.                 |
| `prompt_optional`   | `bool \| None`           | `True`                       | Skip prompting for optional parameters in interactive mode. |
| `add_examples_flag` | `bool`                   | `True`                       | Set to `False` to hide the `--examples` flag.               |
| `add_color_flag`    | `bool`                   | `True`                       | Set to `False` to hide the `--color` / `--no-color` flags.  |

```python
@cmd(description="Deploy the app", version="1.0.0", hidden=True)
def deploy(host: str, port: int = 8080):
    ...
```

#### Usage examples

Pass a `dict[str, str]` of `{description: command}` to show usage examples in `--help`:

```python
@cmd(
    examples={
        "Add two numbers": "calc 1 + 2",
        "Multiply": "calc 2 '*' 3",
    },
    epilog="See the full docs at https://example.com/calc",
)
def calc(a: float, op: str, b: float):
    ...
```

```bash
$ python calc.py --help
usage: calc.py [-h] [--examples] a op b

positional arguments:
  a
  op
  b

options:
  -h, --help    show this help message and exit
  --examples    Show usage examples and exit

examples:
  calc 1 + 2   # Add two numbers
  calc 2 * 3   # Multiply

See the full docs at https://example.com/calc
```

The `--examples` flag prints only the example lines and exits, without the rest of the help text:

```bash
$ python calc.py --examples
calc 1 + 2  # Add two numbers
calc 2 * 3  # Multiply
```

Set `add_examples_flag=False` to suppress the `--examples` flag while keeping examples in `--help`.

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

### Path arguments

`pathlib.Path` annotations are supported natively. Paths are auto-expanded (`~`) and resolved to absolute paths:

```python
from pathlib import Path

def process(data: Path, output: Path = Path("out.txt")):
    ...
```

```bash
python script.py ~/input.csv --output ./results.csv
# Path becomes: /home/user/input.csv
# Output becomes: /cwd/results.csv
```

Set `Spec(path_resolve=False)` to preserve the raw path as provided.

Add validation with `Spec`:

```python
from typing import Annotated
from defcmd.spec import Spec

def read_log(
    log: Annotated[Path, Spec(path_exists=True, path_type="file")],
    out_dir: Annotated[Path, Spec(path_type="dir")] = Path("./logs"),
):
    ...
```

### Interactive mode

Run the script with **no arguments at all**, from a real terminal, and `defcmd` walks through every parameter, prompting for each one in order:

```bash
$ python greet.py
? Name: Alice
✓ Name: Alice
? Times [default: 1]:
✓ Times: 1
? Excited [y/N]: y
✓ Excited: y
HELLO, ALICE!!!
```

- Required parameters keep re-prompting until you enter something; blank input isn't accepted.
- Optional parameters show their default in brackets; pressing Enter accepts it.
- Boolean parameters accept a single keypress (`y` or `n`) or press Enter to accept the default.
- Each prompt is replaced in-place by a `✓` confirmation line on completion.
- `Literal` parameters list the valid choices and accept either the exact value or its number.

When using the advanced `Spec` annotations:
- Parameters with `Spec(prompt="Enter value")` override the default prompt text.
- Parameters with `Spec(prompt=True)` force prompting even when `@cmd(prompt_optional=False)` is set.
- Parameters with `Spec(prompt=False)` skip prompting entirely and use the default value (raises an error if no default exists).
- Parameters with `Spec(secret=True)` hide the input (for passwords, tokens, etc.).
- Parameters with `Spec(help=...)` can override the default help text shown in `--help`.
- Parameters with validation constraints (`min`, `max`, `pattern`) will re-prompt until the value satisfies the constraint.

Interactive mode only triggers when **both** of these are true: 
- no arguments were passed, 
- and stdin is a real terminal (not piped or redirected). 

Running a script with no args in a non-interactive context (cron, CI, piped input) just errors normally instead of hanging waiting for input.

### Help text

The function's docstring is shown as the description in `--help`. Override it with `@cmd(description=...)`:

```python
@cmd(description="Deploy the application to a target host.")
def deploy(host: str):
    ...
```
```bash
$ python deploy.py --help
usage: deploy.py [-h] host

Deploy the application to a target host.

positional arguments:
  host
```

Use `@cmd(epilog=...)` for text after the argument help, and `@cmd(help=...)` for a shorter description used in subcommand listings. Per-parameter help text is set via `Annotated[..., Spec(help=...)]` — see the next section.

### Advanced Parameter Specification

The `Spec` annotations allow you to attach additional metadata to the cli parameters:

```python
from typing import Annotated, Literal
from defcmd import cmd
from defcmd.spec import Spec

@cmd
def action(
        payload: Annotated[Literal["json", "xml", "csv", "html"], Spec(help="The payload to send", prompt="Payload")],
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

| Spec           | Description                                                    | Overrides                    |
| -------------- | -------------------------------------------------------------- | ---------------------------- |
| `short`        | Short flag for the parameter (e.g., `-p`)                      |                              |
| `help`         | Help text for the parameter, shown in `--help`                 | The default help message     |
| `prompt`       | Custom prompt text, `True` to force, `False` to skip           | The default prompt text      |
| `secret`       | If `True`, input is hidden in interactive mode                 |                              |
| `env`          | Environment variable(s) to read a default value from           | The function's default value |
| `min`          | Minimum numeric value (inclusive)                              |                              |
| `max`          | Maximum numeric value (inclusive)                              |                              |
| `pattern`      | A regex pattern the value must match (uses `fullmatch`)        |                              |
| `validate`     | A custom validation function for the parameter                 |                              |
| `path_exists`  | If `True`, raises an error if the path doesn't exist           |                              |
| `path_type`    | `"file"` or `"dir"` - validates the path type                  |                              |
| `path_resolve` | If `True` (default), expands `~` and resolves to absolute path |                              |

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

The `@cli.subcmd` decorator accepts all `@cmd` parameters plus:

| Parameter | Type                | Default       | Description                                                       |
| --------- | ------------------- | ------------- | ----------------------------------------------------------------- |
| `name`    | `str \| None`       | `fn.__name__` | Override the subcommand name.                                     |
| `aliases` | `list[str] \| None` | `None`        | Alternative names for the subcommand (`add_parser(aliases=...)`). |

`CLI(...)` also accepts `description`, `help`, `version`, `examples`, `add_examples_flag`, and `add_color_flag` for the top-level CLI parser.

### Nested subcommands / groups

Use `cli.group()` to create command groups with nested subcommands:

```python
cli = CLI(description="Cloud tool")

# Create a group and register subcommands on it
db = cli.group("db", description="Database commands")

@db.subcmd
def migrate(message: str):
    """Run database migrations"""
    print(f"Running migration: {message}")

@db.subcmd
def seed(count: int = 10):
    """Seed the database"""
    print(f"Seeding with {count} records")

if __name__ == "__main__":
    cli.run()
```

```bash
$ python tool.py --help
usage: tool.py [-h] {db} ...

Cloud tool

positional arguments:
  {db}
    db         Database commands

$ python tool.py db --help
usage: tool.py db [-h] {migrate,seed} ...

Database commands

positional arguments:
  {migrate,seed}
    migrate      Run database migrations
    seed         Seed the database
```

Groups can be nested arbitrarily deep:

```python
container = cli.group("container", description="Manage containers")

@container.subcmd
def run(image: str, detach: bool = False):
    """Run a container"""
    print(f"Running {image}")

logs = container.group("logs", description="View container logs")

@logs.subcmd
def follow(name: str):
    """Follow log output"""
    print(f"Following {name}")
```

```bash
$ python tool.py container run nginx --detach
$ python tool.py container logs follow my_container
```

Interactive mode works with groups, it recursively prompts until it reaches a leaf command, then runs its wizard.

### Environment Variables

Environment variables provide default values that can be overridden by CLI arguments:

```python
from defcmd import cmd
from defcmd.spec import Spec
from typing import Annotated

@cmd
def deploy(
    host: Annotated[str, Spec(env="HOST")],
    port: Annotated[int, Spec(env=("PORT", "APP_PORT"))] = 8080,
):
    ...
```

```sh
$ export HOST=example.com
$ python deploy.py             # uses HOST env var
$ python deploy.py other.com   # CLI arg overrides env
```

If the env var is not set, the function's default (or a required positional error) applies. A tuple tries each variable name in order and uses the first one found. CLI arguments always take precedence over env vars.

### ANSI Color Output

`defcmd` supports colored terminal output automatically:

- **`$NO_COLOR`**: If the [`NO_COLOR`](https://no-color.org/) environment variable is set, ANSI escape sequences are disabled.
- **TTY detection**: If stdout is piped or redirected (not a terminal), colors are disabled automatically.
- **`--color` / `--no-color`**: Both `Cmd` and `CLI` register these flags to override auto-detection. Pass `add_color_flag=False` to suppress them.

```bash
$ python script.py --color       # force color on
$ python script.py --no-color    # force color off
```

The `--color` flag works at any level; pass it before or after the subcommand:

```bash
$ python tool.py --color db migrate "init"
$ python tool.py db migrate --no-color "init"
```

Set `add_color_flag=False` on a command or CLI to hide the `--color` / `--no-color` flags from `--help`:

```python
@cmd(add_color_flag=False)
def greet(name: str):
    ...
```


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
├── examples/
│   ├── 00_basic.py
│   ├── 01_annotated.py
│   ├── 02_subcommands.py
│   ├── 03_nested_subcommands.py
│   └── 04_examples.py
├── src/
│   └── defcmd/
│       ├── __init__.py
│       ├── terminal/           # Terminal Library
│       ├── widgets/            # Interactive Widgets
│       ├── argparser.py        # Argument Parser
│       ├── convert.py          # Type Conversion & Validation
│       ├── interactive.py      # Interactive Prompting Wizard
│       ├── introspect.py       # Function Signature Introspection
│       ├── runner.py           # Command & CLI Runner
│       └── spec.py             # Spec Annotation
├── tests/
│   └── ...
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

to run `pytest-cov` for coverage report:

```sh
uv run pytest --cov=defcmd --cov-report=term-missing # or --cov-report=html
```

The `examples/` directory contains small manual scripts for trying behavior in a real terminal. `examples/00_basic.py` shows the basic API, while `examples/01_annotated.py` shows `Annotated[..., Spec(...)]` metadata such as help text, custom prompts, secret input, and short flags. `examples/04_examples.py` demonstrates usage examples with `@cmd` and `CLI`. These examples are not part of the test suite, but they are useful for manually trying interactive behavior in a real tty.

```sh
uv run python examples/00_basic.py
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
