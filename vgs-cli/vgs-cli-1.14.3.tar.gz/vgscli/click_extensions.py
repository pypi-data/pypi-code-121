import click
from datetime import datetime, timedelta


class Config(object):
    def __init__(self, debug, env):
        self.debug = debug
        self.env = env


# https://gist.github.com/jacobtolar/fb80d5552a9a9dfc32b12a829fa21c0c#file-click_mutually_exclusive_argument-py-L4
class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help_cmd = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help_cmd + (
                ' NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


class Duration(click.ParamType):
    name = 'duration'

    def convert(self, value, param, ctx):
        try:
            delta_unites = {
                'h': 'hours',
                'm': 'minutes',
                's': 'seconds'
            }
            unit = delta_unites[value[-1:].lower()]
            amount = int(value[:-1])
            delta_options = {unit: amount}
            return (datetime.utcnow() - timedelta(**delta_options)).strftime('%Y-%m-%dT%H:%M:%S')
        except TypeError:
            self.fail(
                "expected string for int() conversion, got "
                f"{value!r} of type {type(value).__name__}",
                param,
                ctx,
            )
        except ValueError:
            self.fail(f"{value!r} is not a valid integer", param, ctx)
        except KeyError:
            self.fail("Only integers that end with h, m or s are allowed", param, ctx)


DURATION = Duration()


class DateTimeDuration(click.ParamType):
    name = 'dateduration'

    def __init__(self, formats=None):
        self.formats = formats or [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S'
        ]

    @staticmethod
    def _try_to_parse_date(value, pattern):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            return None

    def convert(self, value, param, ctx):
        for pattern in self.formats:
            if self._try_to_parse_date(value, pattern):
                return value

        if len(str(value)) > 7:
            return self.fail(
                'invalid date format: {}. (choose from {})'.format(
                    value, ', '.join(self.formats)))

        return DURATION.convert(value, param, ctx)


