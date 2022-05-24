from pathlib import Path
from importlib.resources import files
from limonade.data import load_config, truncate_data
from limonade.misc import parse_file
import json

def fix_data():
    args = parse_inputs()
    truncate_data(args.directory, args.base_name, args.cfg)

    
def parse_inputs():
    import argparse

    parser = argparse.ArgumentParser(description='Fix datafile size discrepancy by truncating to smallest common size.')

    parser.add_argument('directory', metavar='datadir', type=str,
                        help='Data directory. A wildcard expression can be given for chainloading several directories.')
    parser.add_argument('-f', '--filename', metavar='file', type=str,
                        help='name of datafile if not the same as datadir. Wildcards can be used, but the file name'
                             'has to be unique.')
    args = parser.parse_args()
    args.directory = Path(args.directory)
    confd = load_config([args.directory], det_name=None, from_global_conf=False)
    args.cfg = confd

    base_name = parse_file(args.directory, args.filename, confd)
    if len(base_name) > 1:
        print('too many data files!')
        print('base_name', base_name)
        print('len', len(base_name))
        raise ValueError
    args.base_name = base_name[0]

    return args

if __name__ == '__main__':

    fix_data()
