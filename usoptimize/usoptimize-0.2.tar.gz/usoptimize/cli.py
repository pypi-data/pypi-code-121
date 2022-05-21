import argparse
import os
import subprocess
import sys

from usoptimize.convert import convert


def cli():
    parser = argparse.ArgumentParser(
        description='A Python CLI UltraStar Song Converter to optimize song files for the web.')
    parser.add_argument('-i', '--input', metavar='<path of songs>', type=str, nargs=1, required=True,
                        help='Filepath of songs that should be converted')
    parser.add_argument('-o', '--output', metavar='<output path>', type=str, nargs=1, required=True,
                        help='Destination directory of converted songs')
    parser.add_argument('-r', '--replace', action="store_true",
                        help='Whether or not to replace old existing files in output dir')

    args = parser.parse_args()

    input_path = args.input[0]
    output_path = args.output[0]

    if not os.path.isdir(input_path) or not os.path.isdir(output_path):
        print('The path specified does not exist')
        sys.exit()

    # check if ffmpeg is installed in path
    try:
        subprocess.run('ffmpeg -version', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print('FFmpeg is not installed in path. Please install it and try again. (Check How to use https://pypi.org/project/usoptimize/')
        sys.exit()

    convert(input_path, output_path, args.replace)
