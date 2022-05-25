import h5py
import pandas
import pathlib
from pathlib import Path
import os
from . import preciso

def HDF5_make(title, inputFileName, res = None, target_path = None, mode = None, temp=True, write_limit=100, nodes=None, n_samples=2, debug=False):
    '''Procedure creating an hdf data file for preciso results
        
    Parameters
    ------------
    

    title: str
        The name of the created file. Make sure its extentsion is '.hdf5'.   
    inputFileName : str or Pathlib.Path
        The location of the input file used for the simulation. The file information will be stored into the hdf created,
        so that the file itself can be discarded afterwards.
    res : Results object
        The results of the precio simulation with the specified arguments.
        By default, the function is running a a standalone, and determine this object calling preciso by itself. 
    target_path : str or Pathlib.Path
        The directory where the HDF5 file will be saved. Default is current directory.
    mode : char
        The opening mode for the HDF5 file. Default is 'x' to prevent overwriting existing data; use 'w' to bypass. 
    temp : bool
        If True (default), PreciSo will run in a temporary folder, and its results files will
        be read and outputed. All files will be discarded at the end.
        If false, `run_input_file` is directly called and output files will be created
        in current working directory.
    write_limit : int
        The maximum size of the files written by PreciSo, in Megabytes. It prevents PreciSo from filling up your computer's hard drive. 
        Default value is 100MB. If `write_limit` is of a type different than `int`, no limit is set. **Windows is not supported**, there will be **no limit on this plateform**.
    nodes : List of int (optional)
        The id of the node(s) for which we want the precipitates distribution. Default is [0].
    
    '''
    if target_path is None:
        target_path = Path('./') 
    if mode is None:
        mode = 'x'
    if nodes is None:
        nodes = [0]

    #Converting an eventual str type target path into a pathlib Path
    target_path = Path(target_path)      

    if not(os.path.exists(target_path)):
        os.mkdir(target_path)
    
    #Initializing the HDF5 file with the simulation input
    F = h5py.File(target_path / title, mode)

    with open(inputFileName, 'r') as input:
        s = input.read()
    F.attrs['input'] = s

    #Saving simulation parameters
    F.attrs['temp'] = int(temp)
    F.attrs['write_limit'] = write_limit
    F.attrs['nodes'] = nodes
    F.attrs['n_samples'] = n_samples
    F.attrs['debug'] = int(debug)
    F.close()

    #Getting reference simulation results
    if res is None:
        res = preciso.runSimulation(inputFileName, temp, write_limit, nodes, n_samples, debug)
    
    #Saving res.precipitation
    F = h5py.File(target_path / title, 'a')
    F.create_group('precipitation')
    F.close()
    for node in res.precipitation:
        res.precipitation[node].to_hdf(target_path / title, 'precipitation/node_' + str(node))
        F = h5py.File(target_path / title, 'a')
        F['precipitation/node_' + str(node)].attrs['header'] = res.precipitation[node].header
        F.close()


    #Saving res.mechanics
    F = h5py.File(target_path / title, 'a')
    F.create_group('mechanics')
    F['mechanics'].attrs['Enabled'] = int(type(res.mechanics) != str)
    F.close()
    if type(res.mechanics) != str:
        for node in res.mechanics:
            res.mechanics[node].to_hdf(target_path / title, 'mechanics/node_' + str(node))
            F = h5py.File(target_path / title, 'a')
            F['mechanics/node_' + str(node)].attrs['header'] = res.mechanics[node].header
            F.close()

    #Saving res.distribution
    F = h5py.File(target_path / title, 'a')
    D = F.create_group('distribution')
    try:
        _ = res.distribution
    except AttributeError :
       D.attrs['Enabled'] = 0
       F.close()
    else:
        D.attrs['Enabled'] = 1
        D.create_group('data')
        D.attrs['n_datapoints'] = res.distribution.n_datapoints
        D.attrs['n_samples'] = res.distribution.n_samples
        F.close()
        for node in res.distribution.data:
            for P in res.distribution.data[node]:
                for step in res.distribution.data[node][P]:
                    
                    res.distribution.data[node][P][step].to_hdf(target_path / title, 'distribution/data/node_' + str(node) +'/precipitate_'+ P +'/step_'+ str(step))

                    #Saving the DataFrame metadata to ensure its storage and for easier access
                    F = h5py.File(target_path / title, 'a')
                    F['distribution/data/node_' + str(node) +'/precipitate_'+ P +'/step_'+ str(step)].attrs['R_star'] = res.distribution.data[node][P][step].R_star
                    F['distribution/data/node_' + str(node) +'/precipitate_'+ P +'/step_'+ str(step)].attrs['time'] = res.distribution.data[node][P][step].time
                    F['distribution/data/node_' + str(node) +'/precipitate_'+ P +'/step_'+ str(step)].attrs['step'] = res.distribution.data[node][P][step].step
                    F.close()
    return

