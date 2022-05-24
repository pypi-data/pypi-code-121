import sys
import os
import click
from .logger import Logger
from .cli_constants import *
import tempfile
from .configs import ConfigOrigin


class MuOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if: list = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (kwargs.get("help", "") + " This option is mutually exclusive with --" + ", --".join(self.not_required_if) + ".").strip()
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt: bool = self.consume_value(ctx, opts)
        for other_param in ctx.command.get_params(ctx):
            if other_param is self:
                continue
            if other_param.human_readable_name in self.not_required_if:
                other_opt: bool = other_param.consume_value(ctx, opts)
                if other_opt:
                    if current_opt:
                        Logger.error(CLI_MESSAGES['ArgumentsMutalExclusive'].format(str(self.name), str(other_param.human_readable_name)))                      
                        print(CLI_MESSAGES['TryHelpWithCommand'].format(ctx.command_path))
                        ctx.abort()
                    else:
                        self.required = None
        return super().handle_parse_result(ctx, opts, args)


# def modify_click_usage_error(main_command):
def modify_click_usage_error():

    def show(self, file=None):
        import sys
        # if file is None:
        #     file = get_text_stderr()
        Logger.error(self.format_message())
        if self.ctx:
            # echo(self.ctx.get_usage() + '\n', file=file, color=color)
            # echo(self.ctx.get_help(), color=self.ctx.color)
            # echo(CLI_MESSAGES['TryHelp'].format(self.ctx.command_path), color=self.ctx.color)
            # Logger.info(CLI_MESSAGES['TryHelpWithCommand'].format(self.ctx.command_path), force=True)
            print(CLI_MESSAGES['TryHelpWithCommand'].format(self.ctx.command_path))
        else:
            ### for some reason self.ctx is None for BadOptionUsage exception, maybe a bug in click package,
            ### hence can't get the command_path
            # for i in dir(self):
            #     print(f"{i}=", getattr(self, i))
            print(CLI_MESSAGES['TryHelp'])

        sys.argv = [sys.argv[0]]
        # main_command()

    click.exceptions.UsageError.show = show


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))
        
class CustomMultiGroup(click.Group):

    def group(self, *args, **kwargs):
        """Behaves the same as `click.Group.group()` except if passed
        a list of names, all after the first will be aliases for the first.
        """
        def decorator(f):
            aliased_group = []
            if isinstance(args[0], list):
                # we have a list so create group aliases
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    grp = super(CustomMultiGroup, self).group(
                        alias, *args[1:], **kwargs)(f)
                    grp.short_help = "Alias for '{}'".format(_args[0])
                    aliased_group.append(grp)
            else:
                _args = args

            # create the main group
            grp = super(CustomMultiGroup, self).group(*_args, **kwargs)(f)

            # for all of the aliased groups, share the main group commands
            for aliased in aliased_group:
                aliased.commands = grp.commands

            return grp

        return decorator


def command_doc(value):
    def _doc(func):
        func.__doc__ = value
        return func
    return _doc


def ConfigOrigin_from_string(ctx, param, value, has_wildcards=False):
    if not value: return
    if value == '-':
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(sys.stdin.read())
            value = f.name
    else:
        if not has_wildcards:
            if not os.path.exists(value):
                raise click.BadParameter(f"'{value}' does not exist.")
    return value

def config_source_from_string(ctx, param, value):
    return ConfigOrigin.from_str(value)
