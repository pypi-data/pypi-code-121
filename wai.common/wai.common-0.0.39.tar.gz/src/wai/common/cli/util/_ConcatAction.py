from argparse import _AppendAction

# Capture the built-in type class as 'type' is an argument to __init__
_type = type


class ConcatAction(_AppendAction):
    """
    Similar to argparse's "append" action but concatenates
    the lists instead of nesting them. Also only returns the
    default value if no option is supplied, rather than
    concatenating into default a la "append".
    """
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        # Default default is an empty list
        if default is None:
            default = []

        # Can't have a default for a required option
        elif required:
            raise ValueError(f"Can't set a default for a required option")

        # Make sure default is a list
        if not _type(default) is list:
            raise TypeError(f"Default value for {ConcatAction.__qualname__} must be "
                            f"a list, but got a {type(default).__qualname__}")

        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = [] if items is self.default else list(items)
        items += values if isinstance(values, list) else [values]
        setattr(namespace, self.dest, items)
