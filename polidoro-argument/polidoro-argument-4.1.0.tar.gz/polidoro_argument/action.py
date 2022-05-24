import argparse
"""
Actions to execute a Argument method or set to execute a Command method
"""


class _Action(argparse.Action):
    def __init__(self, method, positional, var_positional, keyword, var_keyword, remainder=False, **kwargs):

        self.method = method
        self.positional = positional
        self.var_positional = var_positional
        self.keyword = keyword
        self.var_keyword = var_keyword
        self.remainder = remainder

        super(_Action, self).__init__(**kwargs)


class ArgumentAction(_Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Parse positional and keyword arguments and run the Argument method.
        args = []
        kwargs = {}
        for v in values:
            name, _, value = v.partition('=')
            if value:
                kwargs[name] = value
            else:
                args.append(v)

        resp = self.method(*args, **kwargs)
        if resp is not None:
            print(resp)


class CommandAction(_Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from polidoro_argument.polidoro_argument_parser import METHOD_TO_RUN
        # Set to run the Command method with VALUES as positional arguments.
        # Keywords arguments are parsed in PolidoroArgumentParser.parse_args
        setattr(namespace, METHOD_TO_RUN, {
            'method': self.method,
            'args': values,
        })
