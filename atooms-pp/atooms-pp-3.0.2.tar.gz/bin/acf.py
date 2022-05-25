#!/usr/bin/env python

import sys
import numpy
import atooms.postprocessing
from atooms.postprocessing.helpers import linear_grid, logx_grid

def main(fname):
    x = numpy.loadtxt(sys.stdin if fname=='-' else fname, unpack=True)
    t_grid = list(range(0, len(x), 10))
    t = list(range(len(x)))
    x, y, z = postprocessing.correlation.acf(t_grid, 1, t, x)
    for xi, yi in zip(x, y):
        print(xi, yi)

if __name__ == '__main__':

    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('--vacf-samples', action='store',   dest='vacf_samples', default=60,   type='int')
    parser.add_option('--vacf-tmax', action='store',      dest='vacf_tmax', default=1.0, type='float')
    (opts, args) = parser.parse_args()
    
    main('-')
        
