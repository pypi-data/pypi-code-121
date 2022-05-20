# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 10:21:07 2022

@author: zcope
"""

from scipy.io import FortranFile

def fort_import(domain,dat_str):
    '''
    Importing GFortran Unformatted data into 
    # https://symbols.hotell.kau.se/2017/06/04/io-fortran-python/
    https://stackoverflow.com/questions/32362005/python-reading-unformatted-direct-access-fortran-90-gives-incorrect-output
    https://stackoverflow.com/questions/53639058/reading-fortran-binary-file-in-python
    
    This function reads a .dat file into an np.array
    '''
    #print ('----- IMPORTING BULK DENSITY -----')
    data = FortranFile(dat_str,'r','uint32')
    data = data.read_ints('float32').T
    data = data.reshape(domain.nz,domain.ny,domain.nx)
    
    return data

def fort_export(data, dat_str):
    '''
    Note that data in multidimensional arrays is written in row-major order — 
    to make them read correctly by Fortran programs, you need to transpose the
     arrays yourself when writing them.
         -Not needed since I am writing them (nz,ny,nx) instead of (nz,nx,ny)
         -Could also be fixed by starting the arrays in row major order ('F')
           but I haven't experimented to make sure that's true
    
    This function saves np.array to a .dat file
    '''
    #print ('----- EXPORTING BULK DENSITY -----')
    data = data.astype('float32')
    datafile = FortranFile(dat_str,'w','uint32')
    datafile.write_record(data)