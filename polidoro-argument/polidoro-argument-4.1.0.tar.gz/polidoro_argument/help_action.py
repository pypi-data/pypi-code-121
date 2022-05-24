from argparse import SUPPRESS, Action

from polidoro_argument import PolidoroArgumentParser


class HelpAction(Action):

    def __init__(self,
                 option_strings,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help=None):
        super(HelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser: PolidoroArgumentParser, namespace, values, option_string=None):
        if option_string == '-h':
            parser.print_usage()
        else:
            parser.print_help()

        parser.exit()
