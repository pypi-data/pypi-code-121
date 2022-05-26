import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.arguments.command_line_arguments import option_arg_parser
from logger.ConfigureLogger import ConfigureLogger

from automata.Automata import Automata


def start():
    ConfigureLogger()

    command_line_arg_parser = option_arg_parser('persuader-technology-automata')
    args = command_line_arg_parser.parse_args()

    log = logging.getLogger('Automata')
    log.info('automata initialized')

    RedisCacheHolder(args.options)

    conductor = Automata(args.options)
    conductor.start_process_schedule()


if __name__ == '__main__':
    start()
