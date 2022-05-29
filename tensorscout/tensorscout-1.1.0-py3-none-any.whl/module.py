import numpy as np
import pathos.multiprocessing as pathosmp
    

def single_core(tensor, func, core_idx=1):
    '''handles computation in a single core'''
    # print('computing on core #{}'.format(core_idx))
    
    result = func(tensor)

    return result


def multi_core(tensor, func, cores = 2):
    '''split design into parts for each computing core to 
    handle multi-processing tasks'''
    parts = np.array_split(tensor, cores)
    
    'multiprocessing'
    var = pathosmp.ProcessingPool().map\
    (single_core, parts, [func]*cores, list(np.arange(cores)+1))
                    
    're-collect partitioned results from split function'
    results = [ var[i] for i in range(cores)]
    
    'unpack (*)results if output is larger than a single value'
    out = var[0]
    if type(out) not in [float,int,str]:    
        results = np.stack([*results],axis=1) 

    return results


def rebuild(tensor):
    '''re-assemble tensor from parts (multi_core)'''
    tensor = np.array([*tensor])
    *zy,x = tensor.shape
    
    return tensor.reshape((np.multiply(*zy),x))

    
    