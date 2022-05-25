""" Builtin modules for wfGenes """
import numpy as np

def merge_dic(*files):
    
    file_update = {}
    for file in files:
        if isinstance(file, np.number):
            file = dict(file = float(file))
        else:
            file = dict(file = file)
        file_update = {**file, **file_update}
    return file_update
      