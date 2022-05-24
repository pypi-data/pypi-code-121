import argparse
import os

import validators

from stlinmc import minecraft, voxel


def valid_file(parser, choices, fname):
    """function to validate file input

    Args:
        parser (ArgumentParser): ArgumentParser to throw argument error
        choices (tuple[str]): a tuple of file extensions to allow
        fname (str): the file name to validate

    Returns:
        str: the validated file name
    """
    ext = os.path.splitext(fname)[1]
    if ext == '' or ext.lower() not in choices:
        if len(choices) == 1:
            parser.error(f'{fname} doesn\'t end with {choices}')
        else:
            parser.error(f'{fname} doesn\'t end with one of {choices}')
    return fname


def valid_ip(parser, ipin):
    """function to validate ip input

    Args:
        parser (ArgumentParser): ArgumentParser to throw argument error
        ipin (str): the ip address to validate

    Returns:
        str: the validated ip address
    """
    valid = False
    try:
        validators.ip_address.ipv4(ipin)
        valid = True
    except validators.ValidationFailure:
        valid = False
    try:
        validators.url(ipin)
        valid = True
    except validators.ValidationFailure:
        valid = False
    if valid:
        return ipin
    else:
        parser.error(f'\'{ipin}\' is not a valid IP address or URL')


def run_parser():
    """function to parse arguments

    Returns:
        Namespace: populated namespace from arguments
    """
    parser = argparse.ArgumentParser(description='Import STL into Minecraft')
    parser.add_argument(
        'input',
        type=lambda s: valid_file(parser, ('.stl'), s),
        help='Input STL file')
    parser.add_argument(
        'server',
        type=lambda s: valid_ip(parser, s),
        help='Minecraft Server IP')
    parser.add_argument(
        '--port',
        type=int,
        help='Raspberry Juice Port')
    parser.add_argument(
        '--parallel',
        dest='parallel',
        action='store_true',
        help='Disable parallel processing')
    parser.set_defaults(parallel=False)
    parser.set_defaults(port=4711)
    args = parser.parse_args()
    return args


def main():
    """build stl file in specified server
    """
    args = run_parser()
    print(f"Generating voxels from {args.input}")
    voxels = voxel.import_stl_as_voxels(args.input, args.parallel)
    print(f"Sending voxels to {args.server}:{args.port}")
    minecraft.build_voxels(voxels, args.server, args.port, args.parallel)
    print("Sent build commands to server, Done!")


if __name__ == '__main__':
    main()
