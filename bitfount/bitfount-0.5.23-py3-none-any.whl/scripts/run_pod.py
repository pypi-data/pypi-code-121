#!/usr/bin/env python3
"""Script to run a Pod that acts as a compute and data provider."""
from asyncio import get_event_loop
import logging
from os import PathLike
import sys
from typing import Union

import fire

from bitfount.runners.pod_runner import setup_pod_from_config_file
from bitfount.runners.utils import setup_loggers

loggers = setup_loggers([logging.getLogger("bitfount")])


def run(path_to_config_yaml: Union[str, PathLike]) -> None:
    """Runs a pod from a config file."""
    pod = setup_pod_from_config_file(path_to_config_yaml)
    pod.start()


def main() -> None:
    """Script entry point."""
    # If an argument has been provided to the script, we will run in headless mode.
    # The first element in sys.argv is always the script name so to check if any
    # arguments have been provided we check if the length of sys.argv is greater than 1.
    if len(sys.argv) > 1:
        fire.Fire(run)

    # Otherwise we will run in interactive mode (depending on the OS).
    elif sys.platform == "win32":
        import easygui as easygui

        # Windows doesn't work well with wxasync, so using easygui instead of wx.
        filename = easygui.fileopenbox(filetypes=[["*.yaml", "*.yml", "YAML files"]])
        if filename:
            try:
                run(filename)
            except Exception as e:
                print(e)
                sys.exit(1)
        else:
            print("No config file provided.")

    elif sys.platform == "darwin":

        # Skipping analyzing "wxasync": module is installed,
        # but missing library stubs or py.typed marker
        # This is only used for Mac but must be imported here to avoid mypy errors on
        # non-mac platforms.
        import wxasync

        from scripts.pod_ui_utils import Frame

        # Use wxPython if client is not headless
        app = wxasync.WxAsyncApp(redirect=True)
        try:
            Frame().Show()
            loop = get_event_loop()
            loop.run_until_complete(app.MainLoop())

        except Exception as e:
            print(e)
            print("The file provided does not match the required format.")
            sys.exit(1)

    else:
        print(
            f"{sys.platform} OS does not support a GUI. Please run in headless mode "
            f"and provide a config file.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
