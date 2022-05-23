import shlex
import sys
import os
import subprocess as sp

#indir="data/100206/100206_MNI.bundles"
#in_npoints="21" #puede variar, elección del usuario, se recomienda usar a 21 puntos.
#outdir="data/100206/100206_MNI_21p.bundles"
#sp.run(['./sampled_npoints/sliceFibers', indir, outdir, in_npoints])

pathname = os.path.dirname(__file__)


if os.path.exists(pathname + '/sampled_npoints/sliceFibers'):
    print("dbindex exists.")
else:
    print("dbindex does not exist in path. Compiling it: ")
    sp.run(['gcc', pathname + '/sampled_npoints/sliceFibers.c', '-o', pathname + '/sampled_npoints/sliceFibers', '-lm', '-w'])
    
    if os.path.exists(pathname + '/sampled_npoints/sliceFibers'):
        print("Target directory has been created successfully.")

    else: 
        print("Target directory still doesn't exist. Exiting...")
        exit()
        

indir = sys.argv[1]
in_npoints = sys.argv[2] # se recomienda 21
outdir = sys.argv[3]

sp.run([ pathname + '/sampled_npoints/sliceFibers', indir, outdir, in_npoints])
sp.run(['rm', pathname + '/sampled_npoints/sliceFibers'])
