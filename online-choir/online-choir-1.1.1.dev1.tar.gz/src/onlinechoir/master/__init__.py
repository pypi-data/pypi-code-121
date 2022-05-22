
def app():
    """Entry point for the packaged (pyinstaller) app"""
    from onlinechoir.common.log import setup_logging
    from onlinechoir.common.platform import get_log_folder
    from .gui import main
    setup_logging('ERROR', get_log_folder() / "master_gui.log")
    main()


def cli():
    """Entry point for the pure python master client"""
    import argparse

    from onlinechoir.common.log import parse_args_and_set_logger
    from .master_client import main as main_cli
    from .gui import main as main_gui

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no-gui', action="store_true",
                        help="Run the command-line client")
    parser.add_argument('-i', '--input',
                        help="(CLI only) The input audio file")
    parser.add_argument('-s', '--server', default='online-choir.modetexte.ch',
                        help="(CLI only) The address of the server")
    parser.add_argument('-p', '--port', type=int, default=8878,
                        help="(CLI only) The port to connect to (master port)")
    parser.add_argument('-o', '--output',
                        help="(CLI only) Record the session into the given file (WAV or FLAC)")
    parser.add_argument('-x', '--mute', action="store_true",
                        help="(CLI only) Do not play any sound")
    parser.add_argument('-l', '--live', action='store_true',
                        help="(CLI only) Start a live session: use audio input instead of a file")
    parser.add_argument('-m', '--monitor-level', type=float, default=0.1,
                        help="(CLI only) Mix the audio file with the choir with the given gain")
    parser.add_argument('-k', '--skip-seconds', type=float,
                        help="(CLI only) Skip this number of seconds of the audio file")

    parsed_args = parse_args_and_set_logger(parser, 'master')

    if parsed_args.no_gui:
        main_cli(inpt=parsed_args.input,
                 server=parsed_args.server,
                 port=parsed_args.port,
                 output=parsed_args.output,
                 mute=parsed_args.mute,
                 live=parsed_args.live,
                 monitor_level=parsed_args.monitor_level,
                 skip_seconds=parsed_args.skip_seconds)
    else:
        main_gui()
