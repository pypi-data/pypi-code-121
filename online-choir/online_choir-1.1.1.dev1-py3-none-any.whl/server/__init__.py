def cli():
    import argparse
    import asyncio
    import uvloop
    from ..common.log import parse_args_and_set_logger, logger
    from .server import start_server
    parser = argparse.ArgumentParser()
    parser.add_argument('--slave-port', type=int, default=8868, help="Port number where slave clients connect")
    parser.add_argument('--master-port', type=int, default=8878, help="Port number where the master client connects")
    parser.add_argument('--control-port', type=int, default=8858, help="Port number where the mix can be altered")
    parser.add_argument('-m', '--monitor-level', type=float,
                        help="Mix the audio file with the choir with this gain (default: don't mix it)")
    parser.add_argument('-r', '--record-audio', action="store_true", help="Keep a copy of all recordings on the server")
    parser.add_argument('-i', '--ices', help="Create a web radio by passing the given config file to ices2")

    parsed_args = parse_args_and_set_logger(parser, 'server')
    uvloop.install()
    try:
        asyncio.run(start_server(monitor_level=parsed_args.monitor_level,
                                 master_port=parsed_args.master_port,
                                 slave_port=parsed_args.slave_port,
                                 control_port=parsed_args.control_port,
                                 record_audio=parsed_args.record_audio,
                                 ices_config=parsed_args.ices))
    except KeyboardInterrupt:
        logger.info("Done.")
    exit(0)
