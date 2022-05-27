__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
import sys
from argparse import ArgumentError, ArgumentParser, Namespace
from pathlib import Path
from shutil import copy
from typing import Callable, List

from media_tools.util.logging import setup_logging
from media_tools.util.mixcloud import (
    AuthorizationError, create_mix, get_access_token, DEFAULT_CROSSFADE_MS, DEFAULT_MAX_RETRY,
    DEFAULT_AUDIO_FILE_TYPES,
    MixPath
)


def exists(check: Callable) -> Callable:
    def inner(arg: str) -> Path:
        path = Path(arg)
        if not path.exists():
            raise ValueError(f"{arg} does not exist")
        if not check(path):
            raise ValueError(f"{arg} is of wrong type")
        return path
    return inner


def parse_commandline(args: List[str]) -> Namespace:
    kwargs = dict(exit_on_error=False) if sys.version_info >= (3, 9) else {}
    parser = ArgumentParser(
        description="Creates a mix from audio files and uploads it to Mixcloud",
        **kwargs  # type: ignore
    )
    parser.add_argument(
        '-d', '--directory', type=exists(Path.is_dir), required=True,
        help='Directory containing the mix'
    )
    parser.add_argument(
        '-e', '--extensions', nargs='+', default=DEFAULT_AUDIO_FILE_TYPES,
        help='List of extensions considered as audio files for the mix'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true'
    )
    parser.add_argument(
        '-s', '--strict', action='store_true', help='Fail if any required data are missing'
    )
    parser.add_argument(
        '-c', '--crossfade-ms', type=int, default=DEFAULT_CROSSFADE_MS,
        help='Milliseconds overlap between tracks'
    )
    parser.add_argument(
        '-r', '--max-retry', type=int, default=DEFAULT_MAX_RETRY,
        help='Maximum number of retries for failing uploads'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-a', '--auth-token-file', type=exists(Path.is_file),
        help='File containing the Mixcloud auth token'
    )
    group.add_argument(
        '-t', '--auth-token-string', type=str, help='Mixcloud auth token as string'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--description', type=str, help='Description for the mix as string'
    )
    group.add_argument(
        '--description-file', type=exists(Path.is_file),
        help='File containing the description for the mix'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--tags', nargs="*", type=str, help='Tags for the mix as a list of strings'
    )
    group.add_argument(
        '--tags-file', type=exists(Path.is_file),
        help='File containing the tags for the mix, one per line'
    )
    parser.add_argument(
        '--picture-file', type=exists(Path.is_file), help='Picture file for the mix'
    )
    return parser.parse_args(args)


def prep_mix_dir(opts: Namespace) -> None:
    description_file = opts.directory / 'description.txt'
    tags_file = opts.directory / 'tags.txt'
    if opts.description_file:
        copy(opts.description_file, description_file)
    if opts.description:
        with description_file.open('w') as file:
            file.write(opts.description)
    if opts.tags_file:
        copy(opts.tags_file, tags_file)
    if opts.tags:
        with tags_file.open('w') as file:
            file.write('\n'.join(opts.tags))
    if opts.picture_file:
        copy(opts.picture_file, opts.directory)
    check_strict(opts, description_file, tags_file)


def check_strict(opts, description_file, tags_file):
    if not description_file.exists():
        warning_or_error(opts, f'description file {description_file} needed')
    if not tags_file.exists():
        warning_or_error(opts, f'tags file {tags_file} needed')
    if not list(opts.directory.glob('*.*p*g')):
        warning_or_error(opts, f'picture file needed in {opts.directory}')


def warning_or_error(opts, message):
    if opts.strict:
        raise ValueError(message)
    logging.warning(message)


def main() -> None:
    try:
        opts = parse_commandline(sys.argv[1:])
    except ArgumentError as error:
        setup_logging(Namespace())
        logging.error(error)
        sys.exit(1)

    setup_logging(opts)

    try:
        access_token = extract_auth_token(opts)
        prep_mix_dir(opts)

        mix_path = MixPath(Path(opts.directory), tuple(f'*.{ext}' for ext in opts.extensions))
        mix = create_mix(mix_path, access_token, crossfade_ms=opts.crossfade_ms, strict=opts.strict)
        mix.export()
        mix.upload(max_retry=opts.max_retry)
    except (ValueError, AuthorizationError) as error:
        logging.error(error)
        sys.exit(1)
    except KeyboardInterrupt:
        logging.warning('interrupted by user!')


def extract_auth_token(opts: Namespace) -> str:
    if opts.auth_token_string is not None:
        return opts.auth_token_string
    return get_access_token(opts.auth_token_file)


if __name__ == '__main__':
    main()
