# `defcmd`

Turn any Python function signature into a command-line script.

```python
from defcmd import cmd

@cmd
def greet(name: str, times: int = 1, formal: bool = False):
    """Greet a person a specified number of times."""
    for _ in range(times):
        if formal:
            print(f"Hello, {name}.")
        else:
            print(f"Hi, {name}!")

if __name__ == "__main__":
    greet.run()
```

This will create a command-line interface that allows you to call the `greet` function with the appropriate arguments. For example:

```bash
python greet.py --name Alice --times 3 --formal
```
`defcmd` scripts support interactive mode as well, allowing you to call the function without providing any arguments upfront. You can simply run the script and it will prompt you for the inputs:

```bash
$ python greet.py
Name: Alice
Times [1]:   # Leave blank for default value
Formal [y/N]: y
Hello, Alice.
```
Zero external dependencies. Built on `argparse` and `inspect` from the standard library.

---

## Development

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
