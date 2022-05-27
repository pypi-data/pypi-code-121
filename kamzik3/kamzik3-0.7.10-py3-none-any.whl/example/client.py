import argparse
import os
import signal

import oyaml as yaml

import kamzik3
from kamzik3.snippets.snippetsWidgets import init_qt_app

helptext = """
Here should come some explanation about the client.
"""

if __name__ == "__main__":
    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument("--chdir", help="Path to active directory", default="./")
    parser.add_argument(
        "--conf",
        help="Path to configuration file in yaml format",
        default="./conf_dummy_client.yml",
    )
    args = parser.parse_args()

    # Set active directory
    os.chdir(args.chdir)
    # Create PyQT5 application
    app = init_qt_app(enable_hd_scaling=False)

    # Load configuration file
    with open(args.conf, "r") as configFile:
        config = yaml.load(configFile, Loader=yaml.Loader)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if "session_window" in config:
        config["session_window"].show()

    # Start PyQT5 app loop
    app.exec_()

    # Close session
    config["session"].stop()
