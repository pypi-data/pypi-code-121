import os
import h5py

def get_filename(dirct, prefix, suffix, form):
    i = 0
    files = os.listdir(dirct)
    while True:
        fname = prefix + form.format(i) + suffix
        if not (fname in files):
            return fname
        i += 1

def get_hdf(dirct, mask_func):
    files = os.listdir(dirct)
    files_hdf = []
    for f in files:
        if f.endswith('.hdf5'):
            files_hdf.append(f)

    opened_hdf = [] 
    for fh in files_hdf:
        hdf_file = h5py.File(f'{dirct}/{fh}', 'r')
        if mask_func(hdf_file):
            opened_hdf.append(hdf_file)
        else:
            hdf_file.close()
    return opened_hdf
