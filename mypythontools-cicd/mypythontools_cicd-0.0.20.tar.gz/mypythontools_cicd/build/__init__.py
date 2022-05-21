"""
This module build the app via pyinstaller.
It has presets to build applications build with eel.

There is one main function `build_app`. Check it's help for how to use
it (should be very simple).

Note:
    You can run build for example from vs code tasks, create folder utils,
    create build_script.py inside, add

>>> import mypythontools
...
>>> if __name__ == "__main__":
...     mypythontools.build.build_app()  # With all the params you need.

In VS Code you can add this task to global tasks.json to run it with anytime::

    {
        "label": "Build app",
        "type": "shell",
        "command": "python",
        "args": ["${workspaceFolder}/utils/build_script.py"],
        "presentation": {
            "reveal": "always",
            "panel": "new"
        }
    },
"""
from mypythontools_cicd.build.build_internal import build_app

__all__ = ["build_app"]
