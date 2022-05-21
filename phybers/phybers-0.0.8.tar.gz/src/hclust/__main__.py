#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess  as sp
import os
from hclust.hierarchical import clusterTools as CT
import time
import numpy as np
import hclust.read_write_bundle as rb
import shlex

pathname = os.path.dirname(__file__)
exepath = pathname + "/hierarchical"
sp.run(['mkdir', pathname + "/data/hierarch"])
#print(exepath)

if os.path.exists(exepath + "/fiberDistanceMax"):
    #print("Found fibDist executable file. Erasing and compiling again.")
    sp.run(['rm', exepath + "/fiberDistanceMax"])
    sp.run(['gcc', exepath + '/fiberDistanceMax.c', '-o', exepath + '/fiberDistanceMax', '-lm', '-w'])
else:
    print("Executable file not found. Compiling fiberDistanceMax.c")
    sp.run(['gcc', exepath + '/fiberDistanceMax.c', '-o', exepath + '/fiberDistanceMax', '-lm', '-w'])
    if os.path.exists(exepath + "/fiberDistanceMax"):
        print("fiberDistanceMax.c compiled.")
    else: 
        print("Executable file still not found. Exiting")
        exit()
        
if os.path.exists(exepath + "/getAffinityGraphFromDistanceMatrix"):
    #print("Found getAff executable file. Removing and compiling again.")
    sp.run(['rm', exepath + "/getAffinityGraphFromDistanceMatrix"])
    sp.run(['g++', exepath + '/getAffinityGraphFromDistanceMatrix.cpp', '-o', exepath + '/getAffinityGraphFromDistanceMatrix'])
else:
    print("Executable file not found. Compiling getAffinityGraphFromDistanceMatrix.cpp")
    sp.run(['g++', exepath + '/getAffinityGraphFromDistanceMatrix.cpp', '-o', exepath + '/getAffinityGraphFromDistanceMatrix'])
    if os.path.exists(exepath + "/getAffinityGraphFromDistanceMatrix"):
        print("getAffinityGraphFromDistanceMatrix.cpp compiled.")
    else: 
        print("Executable file still not found. Exiting")
        exit()
        
if os.path.exists(exepath + "/getAverageLinkHCFromGraphFile"):
    #print("Found getAvrg executable file. Deleting and compiling again")
    sp.run(['rm', exepath + "/getAverageLinkHCFromGraphFile"])
    sp.run(['g++', exepath + '/getAverageLinkHCFromGraphFile.cpp', '-o', exepath + '/getAverageLinkHCFromGraphFile'])
else:
    print("Executable file not found. Compiling getAverageLinkHCFromGraphFile.cpp")
    sp.run(['g++', exepath + '/getAverageLinkHCFromGraphFile.cpp', '-o', exepath + '/getAverageLinkHCFromGraphFile'])
    if os.path.exists(exepath + "/getAverageLinkHCFromGraphFile"):
        print("getAverageLinkHCFromGraphFile.cpp compiled.")
    else: 
        print("Executable file still not found. Exiting")
        exit()

def Hierarchical(raw_tractography,MatrixDist_output, affinities_graph_output,MaxDistance_Threshold,dendogram_output):
    """
    Run to Hierarchical clustering.

    """
    # Step1. Distance Matrix
    
    t0= time.time()
    #aux_str = "." + exepath + "/fiberDistanceMax " + raw_tractography + " " + MatrixDist_output 
    #sp.run(shlex.split(aux_str), check = True)
    sp.run([pathname + "/hierarchical/fiberDistanceMax", raw_tractography, MatrixDist_output],check = True)
    print("Distance Matrix Delay: ", time.time()-t0, "[s]")

    # Step2. Affinities Graph
    t0= time.time()
    sp.run([pathname + "/hierarchical/getAffinityGraphFromDistanceMatrix", MatrixDist_output, affinities_graph_output, MaxDistance_Threshold])
    print("Affinities Graph Delay: ", time.time()-t0, "[s]")
    
    # Step3. Dendogram   
    t0= time.time()
    sp.run([pathname + "/hierarchical/getAverageLinkHCFromGraphFile",affinities_graph_output,dendogram_output])
    print("Dendogram Delay: ", time.time()-t0, "[s]")
    

#%% Example Hierarchical Clustering

print("---Example Hierarchical Clustering---")
    
#dir_raw_tractography="../data/118225_MNI_21p_sub.bundles" # input format: ".bundles" 
dir_raw_tractography = sys.argv[1] # input format: ".bundles" 
MatrixDist_output= pathname + "/data/hierarch/matrixd.bin" # output format: ".bin" 
affinities_graph_output=pathname + "/data/hierarch/affin.txt"
#MaxDistance_Threshold="40" # variable threshold 
MaxDistance_Threshold = sys.argv[2] # variable threshold 
dendogram_output= pathname + "/data/hierarch/dendogram.txt"
t0= time.time()

Hierarchical(dir_raw_tractography,MatrixDist_output, affinities_graph_output,MaxDistance_Threshold,dendogram_output)

print("Hierarchical Delay: ", time.time()-t0, "[s]")

#%% Function and Example Particional Hierarchical Clustering

def  Particional_Hierarchical(maxdist,var,arbfile,afffile,partfile):
    
    """
       Returns a ".txt" file with the detected clusters, where each list is a cluster.    
       maxdist, 30 or 40mmm is recommended
       var = 3600 ##minimum affinity within a cluster => #  N.exp( -max_cldist * max_cldist / var)
    """
    
    wfv=CT.wforest_partition_maxdist_from_graph( arbfile,maxdist,True,afffile,var)
    
    clusteres=wfv.clusters
        
    ar=open(partfile,'wt')
    ar.write(str(clusteres))
    ar.close()


#Example Particional Hierarchical Clustering
print("---Example Particional Hierarchical Clustering---")

maxdist= float(sys.argv[3]) # define usuario, se recomienda 30?
var = float(sys.argv[4]) # define usuario, pero se recomienda usar 3600.
result_path = sys.argv[5]
arbfile= dendogram_output
afffile= affinities_graph_output
#partfile="../data/hierarch/particion_"+str(maxdist)+".txt" # Path donde se crea el particion_##.txt, crear dentro de carpeta result/ids
partfile= pathname + "/data/hierarch/particion_"+str(maxdist)+".txt" # Path donde se crea el particion_##.txt, crear dentro de carpeta result/ids

Particional_Hierarchical(maxdist,var,arbfile,afffile,partfile)

#%% Function Retrieve clusters of fibers for Hierarchical clustering

def Write_Retrieve_clusters(d_result,wfv):

    """
    Return the clusters in the directory, d_result    
    """ 
    list_clusters=wfv.clusters
    
    raw_tractography = np.array(rb.read_bundle(dir_raw_tractography))
    
    for clus  in range(len(list_clusters)):
        if not os.path.exists(d_result+"/"):
            os.mkdir(d_result+"/")
            
        rb.write_bundle(d_result+"/"+str(clus)+".bundles",raw_tractography[list_clusters[clus]])

#%% Example Retrieve clusters of fibers for Hierarchical clustering
        
print("---Example Retrieve clusters of fibers for Hierarchical clustering---") 
       
#d_result = "../data/hierarch/result"
d_result = result_path
wfv=CT.wforest_partition_maxdist_from_graph( arbfile,maxdist,True,afffile,var)
Write_Retrieve_clusters(d_result,wfv)

t0=time.time()

print ("Demora: ", time.time()-t0 ," [s]" )


