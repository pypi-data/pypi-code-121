import shlex
import sys
import os
import subprocess as sp

#in_imgdef="data/100206/acpc_dc2standard.nii" #importante, dar error si no se entrega
#indir="data/100206/100206.bundles" #importante
#outdir="data/100206/100206_MNI.bundles"
#sp.run(['./deformHCPtoMNI/deform',in_imgdef, indir, outdir])

pathname = os.path.dirname(__file__)

print(pathname)

if os.path.exists(pathname + '/deformHCPtoMNI/deform'):
    print("deform executable exists.")
else:
    print("deform not found in path. Compiling it: ")
    sp.run(['gcc', pathname + '/deformHCPtoMNI/main.c', '-o', pathname + '/deformHCPtoMNI/deform', '-lm', '-w'])
    
    if os.path.exists(pathname + '/deformHCPtoMNI/deform'):
        print("deform executable has been created successfully.")

    else: 
        print("deform executable still not found. Exiting...")
        exit()
        

in_imgdef = sys.argv[1]

if not in_imgdef.endswith('.nii'):
    print("You have to insert a .nii file as the first argument.")
    exit()
    
indir = sys.argv[2]
outdir = sys.argv[3]

print("Running deform...")
sp.run([pathname + '/deformHCPtoMNI/deform', in_imgdef, indir, outdir])
