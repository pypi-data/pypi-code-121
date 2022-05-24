#!/usr/bin/python
""" print efi variables """
import sys
import logging
import optparse

from virt.firmware.varstore import linux


##################################################################################################
# main

def main():
    parser = optparse.OptionParser()
    parser.add_option('-l', '--loglevel', dest = 'loglevel', type = 'string', default = 'info',
                      help = 'set loglevel to LEVEL', metavar = 'LEVEL')
    parser.add_option('-v', '--verbose', dest = 'verbose',
                      action = 'store_true', default = False,
                      help = 'print varstore verbosely')
    parser.add_option('-x', '--hexdump', dest = 'hexdump',
                      action = 'store_true', default = False,
                      help = 'print variable hexdumps')
    parser.add_option('--volatile', dest = 'volatile',
                      action = 'store_true', default = False,
                      help = 'print volatile variables too')
    (options, args) = parser.parse_args()

    logging.basicConfig(format = '%(levelname)s: %(message)s',
                        level = getattr(logging, options.loglevel.upper()))

    varlist = linux.LinuxVarStore.get_varlist(volatile = options.volatile)
    if options.verbose:
        varlist.print_normal(options.hexdump)
    else:
        varlist.print_compact()

    return 0

if __name__ == '__main__':
    sys.exit(main())
