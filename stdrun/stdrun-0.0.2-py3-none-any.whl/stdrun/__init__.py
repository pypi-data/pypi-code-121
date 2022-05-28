r"""
# What is stdrun ?

stdrun starts a new processes and intercepts it's stdout and stderr streams in order to apply custom actions.

The following features are supported:
 - Print stderr messages in red/bold

# How to install ?

```sh
pip install stdrun
```

# How to use ?
```sh
stdrun 'command'
```

# Using stdrun as a Python library

Check the `Run()` documentation for details on how to use it as a library


"""
from .process import Run

__all__ = ["Run"]
