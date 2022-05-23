from ascend.sdk.client import Client  # noqa: F401
from ascend.sdk.version import VERSION

# WIP: just an outline ...

# Poetry is configured to call the `run` method.


def run():
  print(f"hello, world: {VERSION}")


if __name__ == "__main__":
  run()
