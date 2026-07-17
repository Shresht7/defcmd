from defcmd import cmd, Spec
from typing import Annotated

# Example demonstrating list arguments with `list[T]` and Spec validation

# Run this example with:
# - python examples/06_lists.py deploy server1 server2 localhost 192.168.0.101
# - python examples/06_lists.py deploy server1 server2 --ports 8080 3000 8000 5173
# - python examples/06_lists.py deploy 

@cmd
def deploy(
    hosts: list[str],
    ports: Annotated[list[int], Spec(help="Ports to connect to")] = [22, 80, 443],
):
    print('Selected hosts:')
    for host in hosts:
        print(f"  {host}")

    print('Selected ports:')
    for port in ports:
        print(f"  {port}")


if __name__ == "__main__":
    deploy.run()
