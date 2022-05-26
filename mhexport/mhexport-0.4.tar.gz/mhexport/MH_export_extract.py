import numpy
import numpy.fft
from numpy import matrix
from ctypes import *
#from parmIndex import *
import socket
from time import *
from math import *
import string
import os
from xml.dom import minidom
from threading import *
#from Queue import *
import struct
import pandas as pd
from pandas import Series,DataFrame
import matplotlib.pyplot as plt    

masslistPos = [118.086255,119.089393,121.050872,122.052918,322.048121,323.050718,622.02896,623.031895,922.009798,923.012863,
1221.990636,1222.99377,1521.971475,1522.97465,1821.952313,1822.955518,2121.933152,2122.936377,
2421.91399,2422.917231,2721.894828,2722.898082]

masslistNeg = [112.985587,301.998139,601.978977, 1033.988109, 1333.968947, 1633.949786, 1933.930624, 2233.911463, 2533.892301, 2833.873139]

nomlistPos = [118,322,622,922,1222,1522,1822,2122,2422,2722]

nomlistNeg = [113,302,602,1034,1334,1634,1934,2234,2534,2834]


def read_exported_peaks(filename):
    '''  Read data exported by MassHunterExport "Export peaks" command

    :parameter filename:   Full path string to the desired input file. This file will have been created by MassHunterExport, typically with a .dat extension

    :return:               A list containing scan data in the following format

                     [1, peak_list]
                     [2, peak_list]
                     ... etc
                            where each peak_list is a list containing peak data in the following formmat
                                [mass_in_daltons, height, area, width_in_daltons, resolution]

    '''
    scans = []
    f = open(filename, 'r')
    lines = f.readlines()

    scan_number = 0
    peaks = None
    for line in lines:
        if line.startswith('TIME'):
            scan_number += 1
            if peaks: # At the first 'TIME' we don't yet have peaks 
                scans.append([scan_number, peaks])
            peaks = []
            continue
        
        words = line.split(',')
        try:
            if len(words) == 5:
                mass = float(words[0])
                height = int(words[1])
                area = int(words[2])
                width = float(words[3])
                resolution = int(words[4])
                peak_info = [mass, height, area, width, resolution]
                peaks.append(peak_info)
        except:
            print('Error parsing {0}'.format(line)) #what's this?

    # add final scan
    if peaks:
        scans.append([scan_number, peaks])

    f.close()
    return scans

def profilefindMasses(massList,spectraList,maxdelta):
    lm=len(massList)
    out=list()
    for i in range (0,len(spectraList)):
        s=spectraList[i][1]
        outm=list()
        massListIndex=0 
        massSpectraIndex=0
        lsm=len(s)
        candidates=list()
        while ((massSpectraIndex<lsm) and (massListIndex<lm)):
            smass=s[massSpectraIndex][0]
            sabundance=s[massSpectraIndex][1]
            delta=massList[massListIndex]-smass
            if (delta>maxdelta):
                massSpectraIndex=massSpectraIndex+1
                continue
            if (abs(delta)<=maxdelta):
                candidates.append(s[massSpectraIndex])
                massSpectraIndex=massSpectraIndex+1
                continue
            if (-1.0*delta>maxdelta):
                if (len(candidates)>0):
                    peakIndex=findHighestAbundance(candidates)
                    outm.append(candidates[peakIndex])
                    candidates=list()
                massListIndex=massListIndex+1
                continue
        if (len(outm)==0):
            continue
        out.append([i,outm])
    
    #additional to convert the nested list into dataframe   
    mlist_int = [round(x) for x in massList]
    out_df = pd.DataFrame ()
    l = 0
    for t in out:
        out_df.at[l,'scan']= t[0] + 1 # make the scan number consistent with MassHunter      
        
        count = 0
        for s in t[1]:
            while count<len(massList):
                if abs(massList[count]-s[0])<maxdelta:
                    mserror=(s[0]-massList[count])/massList[count]*1000000
                    out_df.at[l,'{0}_m/z'.format(mlist_int[count])]= s[0]
                    out_df.at[l,'{0}_abd'.format(mlist_int[count])]= s[1]
                    out_df.at[l,'{0}_err'.format(mlist_int[count])]= mserror
                    out_df.at[l,'{0}_res'.format(mlist_int[count])]= s[4]
                    count += 1
                    break
                else:
                    count += 1
        l += 1
    
    #out_df.set_index('scan',inplace = True)  
    #out_df = out_df.reset_index()
         
    return out_df

def findHighestAbundance(mlist):
    maxA=mlist[0][1]
    maxIndex=0
    for i in range (1,len(mlist)):
        if (maxA<mlist[i][1]):
            maxIndex=i
            maxA=mlist[i][1]
    return maxIndex

def exportdat2extract(fname,masslist,maxdelta):
    profile = read_exported_peaks(fname)
    extract_out = profilefindMasses(masslist,profile,maxdelta)
    return extract_out

def get_df_stat(dat_file, cycle_name, deltaDa):
    scans = read_exported_peaks(dat_file)
    df = profilefindMasses(masslistPos, scans, deltaDa)
    df['cycle'] = cycle_name
    df_stat = df.describe()
    df_stat_ = df_stat.T
    df_stat_['%RSD'] = df_stat_['std']/df_stat_['mean']*100
    df_stat = df_stat_.T
    df_stat.index.name = 'items'
    df_stat = df_stat.reset_index()
    df_stat['cycle'] = cycle_name
    return df, df_stat


"""
draw resolution
for m in nomlist:
    ax = df_tlppon.plot(x = '%s_abd'%m, y = '%s_res'%m,kind = 'scatter',color = 'red',label = 'TLPP1',logx=True,grid = True, s=3)
    ax = df_tlppoff.plot(x = '%s_abd'%m, y = '%s_res'%m,kind = 'scatter',color = 'blue',label = 'TLPP0',logx=True,grid = True, s=3,ax = ax)
    ax.set_title('%s resolution abundance distribution'%m)
    ax.set_xlabel('%s_abundance'%m)
    ax.set_ylim(20000)
    ax.set_ylabel('%s_resolution (m/fwhm)'%m)
    plt.show()
"""
