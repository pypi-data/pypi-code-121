import argparse

from metainfo.MetaInfo import MetaInfo

from core.arguments.ParseDictionaryArgs import ParseDictionaryArgs


def option_arg_parser(package_name) -> argparse.ArgumentParser:

    meta_info = MetaInfo(package_name)
    version = meta_info.get_version()
    description = meta_info.get_description()

    command_line_argument_parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTIONS]',
        description=description
    )

    command_line_argument_parser.add_argument(
        '-v', '--version', action='version',
        version=f'{command_line_argument_parser.prog} version {version}'
    )

    command_line_argument_parser.add_argument('--options', nargs='*', required=False, help=f'Specific options for {description}.', action=ParseDictionaryArgs)

    return command_line_argument_parser


def url_option_arg_parser(package_name) -> argparse.ArgumentParser:

    meta_info = MetaInfo(package_name)
    version = meta_info.get_version()
    description = meta_info.get_description()

    command_line_argument_parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTIONS]',
        description=description
    )

    command_line_argument_parser.add_argument(
        '-v', '--version', action='version',
        version=f'{command_line_argument_parser.prog} version {version}'
    )

    command_line_argument_parser.add_argument('url', help='URL')

    command_line_argument_parser.add_argument('--options', nargs='*', required=False, help=f'Specific options for {description}.', action=ParseDictionaryArgs)

    return command_line_argument_parser
