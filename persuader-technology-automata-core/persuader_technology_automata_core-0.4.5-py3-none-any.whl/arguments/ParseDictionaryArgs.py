import argparse


class ParseDictionaryArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 0:
            parser.error('argument requires more key, value parameter(s) e.g. KEY=VALUE')
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value
