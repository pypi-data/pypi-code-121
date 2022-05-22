import ROOT
import time
import numpy as np

from quickstats.interface.cppyy.vectorize import np_type_str_maps

def array2root(array_data, fname:str, tree_name:str, multithread:bool=True):
    if (not ROOT.IsImplicitMTEnabled()) and (multithread):
        ROOT.EnableImplicitMT()
    elif (ROOT.IsImplicitMTEnabled()) and (not multithread):
        ROOT.DisableImplicitMT()
    columns = list(array_data.keys())
    snapshot_templates = []
    for column in columns:
        template_type = np_type_str_maps.get(array_data[column].dtype, None)
        if template_type is None:
            raise ValueError(f"unsupported array type \"{array_data[column].dtype}\"")
        snapshot_templates.append(template_type)
    snapshot_templates = tuple(snapshot_templates)
    df = ROOT.RDF.MakeNumpyDataFrame(array_data)
    df.Snapshot.__getitem__(snapshot_templates)(tree_name, fname, columns)