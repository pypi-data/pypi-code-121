# command-line interface
import sys
from pathlib import Path

from newpyter.ContentsManager import NewpyterContentsManager


def to_paths(files, suffix):
    files = [Path(f).absolute() for f in files]
    for f in files:
        assert f.exists(), f'file {f} does not exist'
        assert f.suffix == suffix, (f.suffix, suffix)
    return files


manager = NewpyterContentsManager()
manager.root_dir = '/'


def print_usage():
    print('Usages:')
    print('python -m newpyter --to ipynb file1 file2 file3')
    print('python -m newpyter --to newpy file1 file2 file3')


def main():
    if len(sys.argv) < 4:
        print_usage()
        exit(1)

    _, command, output_format, *files = sys.argv
    if command != '--to' or (output_format not in ['ipynb', 'newpy']):
        print_usage()
        exit(1)

    input_suffix = {'ipynb': '.newpy', 'newpy': '.ipynb'}[output_format]

    files = to_paths(files, input_suffix)
    for file in files:
        print('processing', file)
        manager.convert_from_newpy_to_ipynb_or_reverse(
            str(file),
            str(file.with_suffix(f'.{output_format}')),
        )


if __name__ == '__main__':
    main()
