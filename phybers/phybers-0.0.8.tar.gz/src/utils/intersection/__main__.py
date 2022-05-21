import shlex
import sys
import os
from subprocess import run
import ffclust.FibersTools.FibersTools as fb
#%% 7. Intersección para ello se usa la función que se muestra a continuación (inter2bundles) realizada en python y esta ejecuta un programa de c que calcula
# que se llama "fiberDistanceMax2bun.c"

pathname = os.path.dirname(__file__)

def inter2bundles (dir_fib1,dir_fib2,outdir, d_th):
    """Calculate the intersection between two sets of fibers.
    """
    # Name de los conjuntos de fibras a comprar
    labelsb1 = os.path.split(dir_fib1)[1] # name of fiber set 1 (m rows)    
    labelsb2= os.path.split(dir_fib2)[1]  # name of fiber set 2 (n columns)
    
    
    p1=0 # constantes para guardar los porcentajes de intersección del input 1
    p2=0 # constantes para guardar los porcentajes de intersección del input 2

    for b1 in labelsb1:
        for b2 in labelsb2:
            
            str_out=b1.split('.')[0]+'-'+b2.split('.')[0] # Construyendo nombre para la matriz de intersección.
                  
            outfile=outdir+str_out+'.txt'
            
            
            # Sie ejecuta el script en C que calcula la distancia euclidiana entre dos bundles.
            
            sp.run([ pathname + '/dinter/fiberDistanceMax2bun', dir_fib1, dir_fib2, outfile])
    
            ar=open(outfile,'rt')
            t=ar.readlines();ar.close()
            m=len(t) # m > num de filas
            n=len(t[0].split('\t')[:-1]) # num > num columnas
            
            M = N.zeros((m,n),dtype = 'float32')
            
            for i in range(m):
                fila=t[i][:-1].split('\t')[:-1]
                for j in range(n):
                    M[i,j]=float(fila[j])
            
            F_under_th=N.where( M < d_th) # fibers with at least 1 other fiber has distance under the threshold
            xp1=list(set(F_under_th[0]))
            yp2=list(set(F_under_th[1]))
            
    
            
            p1=(len(xp1)/fb.getBundleSize(dir_fib1))*100#porcentaje b1
            p2=(len(yp2)/fb.getBundleSize(dir_fib2))*100#porcentaje b2
            
            return (p1,p2)


# Directorios de los dos set de fibras a comprarar


dir_fib1 = sys.argv[1]
dir_fib2 = sys.argv[2]
outdir= sys.argv[3] # este dir es para guardar cálculos como la matriz


d_th = sys.argv[4] # umbral de intersección en milimetros y lo define el usuario. default: 15

if os.path.exists(pathname + '/dinter/fiberDistanceMax2bun'):
    print("Executable found.")
else:
    print("Executable not found in path. Compiling it: ")
    sp.run(['gcc', pathname + '/dinter/fiberDistanceMax2bun.c', '-o', pathname + '/dinter/fiberDistanceMax2bun', '-lm'])
    
    if os.path.exists(pathname + '/dinter/fiberDistanceMax2bun'):
        print("Executable has been created successfully.")

    else: 
        print("Executable still not found. Exiting...")
        exit()

pinter = inter2bundles (dir_fib1, dir_fib2, outdir, d_th)
print ("Intersection in the set of fibers1 [%]: ", pinter[0])
print ("Intersection in the set of fibers2 [%]:: ", pinter[1])


t0=time.time()

print ("Demora: ", time.time()-t0 ," [s]" )



 
