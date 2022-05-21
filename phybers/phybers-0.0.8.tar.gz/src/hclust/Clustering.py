#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess  as sp
import os
from hierarchical import clusterTools as CT
import time
import numpy as np
import read_write_bundle as rb

def Hierarchical(raw_tractography,MatrixDist_output, affinities_graph_output,MaxDistance_Threshold,dendogram_output):
    """
    Run to Hierarchical clustering.

    """
    # Step1. Distance Matrix
    t0= time.time()
    sp.run(["./hierarchical/fiberDistanceMax", raw_tractography, MatrixDist_output],check = True)
    print("Distance Matrix Delay: ", time.time()-t0, "[s]")

    # Step2. Affinities Graph
    t0= time.time()
    sp.run(["./hierarchical/getAffinityGraphFromDistanceMatrix", MatrixDist_output, affinities_graph_output, MaxDistance_Threshold])
    print("Affinities Graph Delay: ", time.time()-t0, "[s]")
    
    # Step3. Dendogram   
    t0= time.time()
    sp.run(["./hierarchical/getAverageLinkHCFromGraphFile",affinities_graph_output,dendogram_output])
    print("Dendogram Delay: ", time.time()-t0, "[s]")
    

#%% Example Hierarchical Clustering

print("---Example Hierarchical Clustering---")
    
dir_raw_tractography="../data/118225_MNI_21p_sub.bundles" # input format: ".bundles" 

MatrixDist_output="../data/hierarch/matrixd.bin" # output format: ".bin" 

affinities_graph_output="../data/hierarch/affin.txt"

MaxDistance_Threshold="40" # variable threshold 

dendogram_output="../data/hierarch/dendogram.txt"

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

maxdist=30 
var = 3600 
arbfile="../data/hierarch/dendogram.txt"
afffile="../data/hierarch/affin.txt"
partfile="../data/hierarch/particion_"+str(maxdist)+".txt"

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
       
d_result = "../data/hierarch/result"
wfv=CT.wforest_partition_maxdist_from_graph( arbfile,maxdist,True,afffile,var)
Write_Retrieve_clusters(d_result,wfv)


