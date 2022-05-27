import argparse
import os
import signal

import oyaml as yaml

import kamzik3
from kamzik3.snippets.snippetsWidgets import init_qt_app

helptext = """
Here should come some explanation about the server.
"""

if __name__ == "__main__":
    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf",
        help="Path to configuration file in yaml format",
        default="./conf_dummy_server.yml",
    )
    parser.add_argument("--chdir", help="Path to active directory", default="./")
    args = parser.parse_args()

    # Set active directory
    os.chdir(args.chdir)
    # Create PyQT5 APPLICATION
    app = init_qt_app(enable_hd_scaling=False)

    # Load configuration file
    with open(args.conf, "r") as configFile:
        config = yaml.load(configFile, Loader=yaml.Loader)
    # Start control loop for devices specified in configuration file
    config["session"].set_config(args.conf)
    config["session"].start_control_loops()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if "session_window" in config:
        config["session_window"].show()

    # Start PyQT5 app loop
    app.exec_()

    # Close session
    config["session"].stop()
