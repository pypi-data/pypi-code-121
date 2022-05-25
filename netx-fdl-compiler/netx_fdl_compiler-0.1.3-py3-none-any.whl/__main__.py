from .fdlconverter import FlashDeviceLabel

import argparse
from yaml import load, dump, Loader, Dumper

def dofdlcompile(ifile, output):
    d = load(ifile, Loader=Loader)
    fdl = FlashDeviceLabel.fromdict(d)
    b = fdl.tobin()
    output.write(b)

def dofdldecompile(ifile, ofile):
    fdl = FlashDeviceLabel.frombin(ifile)
    d = fdl.todict()
    odata = dump(d, Dumper=Dumper, sort_keys=False)
    ofile.write(odata)

parser = argparse.ArgumentParser(usage='fdl_editor [options]')
#parser.add_argument('-V', '--version', action='version', version='0.0.1', help='Print version info and exit')

subparsers = parser.add_subparsers(help='sub-command help', required=True)

fdlcompile = subparsers.add_parser('compile', description='Create a flash device label from a YAML document')
fdlcompile.add_argument('input', help='Input YAML file', type=argparse.FileType('r'))
fdlcompile.add_argument('output', help='Output binary image', type=argparse.FileType('wb'))
fdlcompile.set_defaults(func=dofdlcompile)

fdldecompile = subparsers.add_parser('decompile', description='Convert a binary flash label to a YAML document')
fdldecompile.add_argument('input', help='Input binary image', type=argparse.FileType('rb'))
fdldecompile.add_argument('output', help='Output yaml file', type=argparse.FileType('w'))
fdldecompile.set_defaults(func=dofdldecompile)

args = parser.parse_args()

args.func(args.input, args.output)
    