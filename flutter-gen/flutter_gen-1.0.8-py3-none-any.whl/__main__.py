# PYTHON_ARGCOMPLETE_OK

import sys
from arghandler import subcmd, ArgumentHandler
from flutter_gen.create.create_i18n import CreateI18NCommand


from flutter_gen.figma.generate_text import FigmaGenerateTextCommand
from flutter_gen.config.config_cmd import ConfigCommand
from flutter_gen.generate.generate_image_cmd import GenerateImageCommand
from flutter_gen.generate.generate_localization_cmd import GenerateLocalizationCommand
from flutter_gen.generate.generate_object_mapper_cmd import GenerateObjectMapperCommand
from flutter_gen.generate.generate_router_cmd import GenerateRouterCommand
from flutter_gen.generate.sync_cmd import RunCommand
from flutter_gen.create.create_cmd import CreateCommand
from flutter_gen.generate.watch_cmd import WatchCommand
from flutter_gen.intellji.install_cmd import InstallCommand
from flutter_gen.rename.rename_cmd import RenameCommand
from flutter_gen.template.api_template import APITemplate
from flutter_gen.template.template_cmd import TemplateCommand
from flutter_gen.utils.intellij import Intellij
from . import __version__


@subcmd("template", help="create template files for a scene")
def cmd_template(parser, context, args):
    parser.description = "Create template files for a scene"
    parser.add_argument("type", nargs=1, choices=[
                        "base"], help="template type")
    parser.add_argument("name", nargs=1, help="scene name")
    parser.add_argument(
        "--navigator", required=False, action="store_true", help="Register navigator"
    )
    args = parser.parse_args(args)
    template_name = args.type[0]
    scene_name = args.name[0]
    options = {
        "navigator": args.navigator
    }
    TemplateCommand(template_name, scene_name, options).create_files()


@subcmd('api', help='create input and output files for an API')
def cmd_api(parser, context, args):
    parser.description = 'Create input and output files for an API.'
    parser.add_argument(
        'name',
        nargs=1,
        help='api name'
    )
    args = parser.parse_args(args)
    APITemplate(args.name[0]).run()


@subcmd("i18n", help="i18n")
def cmd_template(parser, context, args):
    parser.description = "i18n"
    parser.add_argument(
        'key',
        nargs=1,
        help='document path'
    )
    parser.add_argument(
        'text',
        nargs=1,
        help='document path'
    )
    args = parser.parse_args(args)
    CreateI18NCommand(args.key[0], args.text[0]).create()


@subcmd("watch", help="watching the file system for updates and rebuilding as appropriate")
def cmd_template(parser, context, args):
    parser.description = "Watching the file system for updates and rebuilding as appropriate"
    WatchCommand().run()


@subcmd("install", help="")
def cmd_template(parser, context, args):
    parser.description = ""
    InstallCommand().run()


@subcmd("run", help="run")
def cmd_template(parser, context, args):
    parser.description = "run"
    parser.add_argument(
        'path',
        nargs=1,
        help='document path'
    )
    args = parser.parse_args(args)
    RunCommand(args.path[0]).run()


def exit_handler():
    Intellij.getInstance().to_file()


def main():
    handler = ArgumentHandler(
        use_subcommand_help=True,
        enable_autocompletion=True,
        epilog="Get help on a subcommand: flutter_gen subcommand -h",
    )
    handler.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
        help="show the version number",
    )
    if len(sys.argv) == 1:
        handler.run(["-h"])
    else:
        handler.run()
    exit_handler()


if __name__ == "__main__":
    main()
