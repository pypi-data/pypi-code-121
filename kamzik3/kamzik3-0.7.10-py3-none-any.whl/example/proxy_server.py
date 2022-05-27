import argparse
import os
import signal
from multiprocessing import Event

import oyaml as yaml

import kamzik3
from kamzik3.devices.deviceSession import server_process
from kamzik3.snippets.snippetsWidgets import init_qt_app

helptext = """
Here should come some explanation about the proxy-server.
"""

stopped = Event()

if __name__ == "__main__":
    # Create sub server processes
    server_A = server_process("./conf_multi_server_A.yml", stopped)
    server_B = server_process("./conf_multi_server_B.yml", stopped)
    # Start both servers
    server_A.start()
    server_B.start()

    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf",
        help="Path to configuration file in yaml format",
        default="./conf_proxy_server.yml",
    )
    parser.add_argument("--chdir", help="Path to active directory", default="./")
    args = parser.parse_args()

    # Set active directory
    os.chdir(args.chdir)
    # Create PyQT5 application
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
    # Set stop event
    stopped.set()
    # Wait for Server A and B to close
    server_A.join()
    server_B.join()
