# `defcmd`

Turn any Python function signature into a command-line script.

```python
from defcmd.runner import cmd

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
from defcmd.runner import cmd

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

`bool` parameters are always flags, never positionals — even if required. They support both the on and off form:

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

Per-parameter help text (and richer parameter metadata via `Annotated`) is planned but not yet implemented.

### What's not supported (yet)

- `*args` and `**kwargs` in the decorated function's signature raises an error at decoration time.
- Per-parameter help text in `--help`.
- Subcommands (multiple `@cmd`-decorated functions in one program).

---

## 🚧 Development

### Syncing dependencies

```sh
uv sync
```

### Testing

```sh
uv run pytest
```
---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
