def app():
    """Entry point for the packaged (pyinstaller) app"""
    from onlinechoir.common.log import setup_logging
    from onlinechoir.common.platform import get_log_folder
    from .gui import main
    setup_logging('ERROR', get_log_folder() / "slave_gui.log")
    main()


def cli():
    """Entry point for the pure python slave client"""
    import argparse

    from onlinechoir.common.log import parse_args_and_set_logger
    from .slave_client import main as main_cli
    from .gui import main as main_gui

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no-gui', action="store_true",
                        help="Run the command-line client")
    parser.add_argument('-s', '--server', default='localhost',
                        help="(CLI only) The address of the server")
    parser.add_argument('-p', '--port', type=int, default=8868,
                        help="(CLI only) The port number to be used on the server (slave port)")
    parser.add_argument('-l', '--latency', type=int, default=5,
                        help="(CLI only) The latency of the audio hardware (to be measured separately)")

    parsed_args = parse_args_and_set_logger(parser, 'slave')

    if parsed_args.no_gui:
        main_cli(server=parsed_args.server, port=parsed_args.port, latency=parsed_args.latency)
    else:
        main_gui()
