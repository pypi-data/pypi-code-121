import click
import os
import sys
from .base import create_app, create_project, tpls
import re
import subprocess
from flask.cli import with_appcontext, FlaskGroup, cli
import importlib


class DefaultCommandGroup(click.Group):
# class DefaultCommandGroup(FlaskGroup):
    """allow a default command for a group"""
    def main(self, *args, **kwargs):

        try:
            importlib.import_module(os.getenv("FLASK_APP", "app"))
        except ModuleNotFoundError:
            pass
            
        return click.Group.main(self, *args, **kwargs)

    def command(self, *args, **kwargs):
        default_command = kwargs.pop('default_command', False)
        if default_command and not args:
            kwargs['name'] = kwargs.get('name', '<>')
        decorator = super(
            DefaultCommandGroup, self).command(*args, **kwargs)

        if default_command:
            def new_decorator(f):
                cmd = decorator(f)
                self.default_command = cmd.name
                return cmd

            return new_decorator

        return decorator

    def resolve_command(self, ctx, args):
        try:
            # test if the command parses
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.UsageError:
            # command did not parse, assume it is the default command
            args.insert(0, self.default_command)
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)
    

@click.group(cls=DefaultCommandGroup, help="Builer Web Services.", invoke_without_command=True)
@click.pass_context
def boa_cli(ctx):

    if not ctx.invoked_subcommand:
        bin_list()


# # cargar los comandos de flask
# for group_name in cli.list_commands({}):
#     group_cmd = cli.get_command({}, group_name)
#     boa_cli.add_command(group_cmd)


@boa_cli.command(
    default_command=True,
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        # allow_interspersed_args:False
    },
)
@click.argument('args', nargs=-1)
def default(args):
    """Command run without a command"""
    if args:
        bin_run(args)


@boa_cli.command()
@click.argument(
        "project",
        default=os.getcwd(),
        # help="Direccion del proyecto.",
)
@click.option(
        "--app",
        "app",
        default="main",
        help="Nombre de la app default",
)
def init(project, app="main"):
    create_project(project, app)
    click.echo(click.style('OK!', fg='green'))

def callback(ctx, param, value):
    print(ctx, param, value)
    if not value and param:
        ctx.abort()

@boa_cli.command()
@click.argument(
        "name",
        # prompt='Escribe el nomnbre de la aplicación',
        # help="Nombre de la app",
)
@click.option(
        "--dir",
        default=os.getcwd() + "/app",
        help="Nombre de la app default",
)
def add_app(name, dir,):
    if not name:
        print("name is required")
        return
    create_app(dir, name)
    click.echo(click.style('OK!', fg='green'))


@boa_cli.command(name="list")
def bin_list():
    path_bin = os.path.join(os.getcwd(), "bin")
    if os.path.exists(path_bin):
        regex = r"^cmd_([\w\d\_\-]+)\("
        with open(path_bin, "r") as bin:    
            matches = re.findall(regex, bin.read(), re.MULTILINE)
            for match in matches:
                click.echo(f"- {match}")


def common_options(f):
    regex = r"[\-]+"
    if sys.argv[1] == "run":
        argv = sys.argv[3:]
    else:
        argv = sys.argv[2:]

    options_str = " ".join(argv)
    options = re.split(regex, options_str)
    options = filter(lambda d: d, options)
    for option in options:
        # print("option", option)
        if "=" in option:
            option = option.strip().split("=")
        else:
            option = option.strip().split()
        if len(option) == 1:
            f = click.option(
                f"-{option[0]}", f"--{option[0]}",
                is_flag=True
            )(f)
        else:
            f = click.option(
                f"-{option[0]}",f"--{option[0]}",
            )(f)
    return with_appcontext(f)


@boa_cli.command(
    name="run",
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        # allow_interspersed_args:False
    },
)
@click.argument(
    "script",
)
@click.argument(
    "extra",
    nargs=-1
)
# @common_options
def bin_run(script, extra, **kargs):
    if sys.argv[1] == "run":
        argv = sys.argv[2:]
    else:
        argv = sys.argv[1:]
    path_bin = os.path.join(os.getcwd(), "bin")
    
    if os.path.exists(path_bin):
        
        regex = fr"^cmd_{re.escape(script)}\("
        with open(path_bin, "r") as bin:
            matches = re.findall(regex, bin.read(), re.MULTILINE)
            if len(matches) > 0:
                subprocess.run(
                    # ["bash", "bin", script] + list(extra),
                    ["bash", "bin"] + argv,
                )
            else:
                click.echo(click.style(f'Command [{script}] no found!', blink=True))
    else:
        click.echo(click.style(f'bin no found!', blink=True))



@boa_cli.command(name="reset-bin")
def bin_reset():
    path_bin = os.path.join(os.getcwd(), "bin")
    
    with open(path_bin, "w") as bin:    
        bin.write(tpls.bin)
    
    click.echo(click.style(f'reset!', blink=True))