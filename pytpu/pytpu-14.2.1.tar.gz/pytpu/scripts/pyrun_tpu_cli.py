import argparse
import logging
import os
from pytpu.tools.helpers import get_io_from_bin
from pytpu.tools.tpu_runner import TpuRunner
# from pytpu.tools.pyrun_tpu import pyrun_tpu

LOGGER = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(prog='pyrun_tpu',
                                     description='Python command line tool to run tpu programs')

    parser.add_argument('-p', nargs='?', help='Path to the program.tpu', type=str)
    parser.add_argument('-i', nargs='?', help='Inputs binary files path', type=str, default='')
    parser.add_argument('-o', nargs='?', help='Save output binary files path', type=str, default='')
    parser.add_argument('-t', nargs='?', help='Enable execution time calculation', type=str)
    parser.add_argument('-debug', help='Enable DEBUG messages', action='store_true')
    parser.add_argument('-pyproc', action='store_true', help='Enable python pre- and post-processing')

    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)
    LOGGER.info(f'Use logging level: {log_level}')

    if args.i is None:
        LOGGER.info('WARNING: no input files are set')
        inputs = []
    else:
        inputs = args.i.split(',')
    input_data, _ = get_io_from_bin(args.p, inputs, 'inputs')

    runner = TpuRunner(program_path=args.p,
                       loop=None,
                       sync=False,
                       pyprocessing=args.pyproc)
    output_data = runner(input_data)
    # output_data = pyrun_tpu(args.p, input_data)

    # Write outputs to binary files
    if args.o is None:
        LOGGER.info('WARNING: no output files are set to store the results')
    else:
        output_files = args.o.split(',')
        _, output_names = get_io_from_bin(args.p, None, 'outputs')
        for idx, name in enumerate(output_names):
            if not os.path.exists(os.path.dirname(output_files[idx])):
                os.makedirs(os.path.dirname(output_files[idx]))
            with open(output_files[idx], 'wb') as io_file:
                io_file.write(output_data[name].tobytes())
                LOGGER.info(f'Writing output {name} to {output_files[idx]}')
