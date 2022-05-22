from typing import Optional, Dict, List, Union
import os
import glob
import time

import numpy as np

import ROOT
import quickstats

root_type_str_maps = {
    'Char_t'    : 'char',
    'Bool_t'    : 'bool',
    'Float_t'   : 'float',
    'Double_t'  : 'double',
    'Int_t'     : 'int',
    'Long_t'    : 'long',
    'Long64_t'  : 'long long',
    'UInt_t'    : 'unsigned int',
    'ULong_t'   : 'unsigned long',
    'ULong64_t' : 'unsigned long long'
}

def rtype2ctype(rtypes:List[str]):
    ctypes = []
    for rtype in rtypes:
        #rtype = rtype.replace("ROOT::VecOps::RVec", "vector")
        ctype = root_type_str_maps.get(rtype, rtype)
        ctypes.append(ctype)
    return ctypes

def templated_rdf_snapshot(rdf:ROOT.RDataFrame, columns:List[str]=None):
    if columns is None:
        columns = [str(i) for i in rdf.GetColumnNames()]
    rtypes = [rdf.GetColumnType(c) for c in columns]
    ctypes = tuple(rtype2ctype(rtypes))
    snapshot = rdf.Snapshot.__getitem__(ctypes)
    return snapshot

def is_corrupt(f:Union[ROOT.TFile, str]):
    if isinstance(f, str):
        f = ROOT.TFile(f)
    if f.IsZombie():
        return True
    if f.TestBit(ROOT.TFile.kRecovered):
        return True
    if f.GetNkeys() == 0:
        return True
    return False

def release_tfiles():
    for f in ROOT.gROOT.GetListOfFiles():
        f.Close()

def compile_macro(name:str, opt:str="kfOc"):
    macros_dir = os.path.join(quickstats.macro_path, 'macros', name)
    macros_path = os.path.join(macros_dir, name + '.cxx')
    print('INFO: Compiling macro "{}"...'.format(name))
    if not os.path.exists(macros_path):
        print('ERROR: Cannot locate macro files from {}. ROOT macros will not be compiled.'.format(macros_dir))
        return -1
    status = ROOT.gSystem.CompileMacro(macros_path, opt)
    #status = ROOT.gROOT.LoadMacro('{}++'.format(macros_path))
    return status

def load_macro(name:str):
    import cppyy
    if name in dir(cppyy.gbl):
        return None
    auto_load = ROOT.gInterpreter.AutoLoad(name)
    # already loaded by quickstats / third-party
    if auto_load == 1:
        return None
    class_loaded = hasattr(ROOT, name)
    if class_loaded:
        return None
    macros_dir = os.path.join(quickstats.macro_path, 'macros', name)
    macros_path = os.path.join(macros_dir, name + '_cxx')
    if not os.path.exists(macros_path + '.so'):
        status_compile = compile_macro(name)
    status_load = ROOT.gSystem.Load(macros_path)
    if (status_load != 0) and (status_load != 1):
        raise RuntimeError(f"Shared library for the macro {name} is incompatible with the current pyROOT version. "
                           "Please recompile by typing \"quickstats compile\". "
                           "(use quickstats.compile_macros() instead inside a jupyter kernel)")
    return status_load

def get_macro_dir(name:str):
    return os.path.join(quickstats.macro_path, 'macros', name)

def get_macro_TClass(name:str):
    if not getattr(ROOT, name):
        raise RuntimeError(f"class {name} is not loaded into ROOT yet")    
    cls = ROOT.TClass.GetClass(name)
    macro_dir = get_macro_dir(name)
    macro_decl_file = os.path.join(f"{macro_dir}/{name}.h")
    macro_impl_file = os.path.join(f"{macro_dir}/{name}.cxx")
    if not os.path.exists(macro_decl_file):
        raise FileNotFoundError(f"decl file {macro_decl_file} for the macro \"{name}\" not found")
    if not os.path.exists(macro_impl_file):
        raise FileNotFoundError(f"impl file {macro_impl_file} for the macro \"{name}\" not found")        
    cls.SetDeclFile(macro_decl_file, 0)
    cls.SetImplFileName(macro_impl_file)
    return cls

def print_resource_used(start):
    proc_info = ROOT.ProcInfo_t()
    flag = ROOT.gSystem.GetProcInfo(proc_info)
    if flag < 0:
        return None
    cpu_time = proc_info.fCpuUser + proc_info.fCpuSys
    wall_time = time.time()-start
    print('Resources Used: cpu_time={:.3f}s, mem={}kb, vmem={}kb, wall_time={:.3f}s'.format(
          cpu_time, proc_info.fMemResident, proc_info.fMemVirtual, wall_time))
    return None

def process_uproot_array(source):
    result = np.array(source)
    if (result.dtype == np.dtype('O')) and (isinstance(result[0], bytes)):
        result = result.astype(str)
    return result

def get_data_size(data):
    if isinstance(data, (tuple, list, np.ndarray)):
        return len(data)
    else:
        return 1

def uproot_to_dict(file):
    result = {}
    for tree in file.values():
        tree_name = tree.name.decode('utf-8')
        result[tree_name] = {}
        for branch in tree.values():
            branch_name = branch.name.decode('utf-8')
            arr = process_uproot_array(branch.array())
            value = arr[0] if len(arr) == 1 else arr
            result[tree_name][branch_name] = value    
    return result
    
def get_leaf_type_str(data):
    from six import string_types
    
    type_str = None
    data_type = None

    if isinstance(data, (tuple, list, np.ndarray)):
        data_type = type(data[0])
        if data_type in string_types:
            return None
    elif isinstance(data, string_types):
        return None
    else:
        data_type = type(data)
        
    if data_type in [float, np.float64]:
        type_str = 'D'
    elif data_type in [int, np.int64]:
        type_str = 'L'
    elif data_type in [np.int32]:
        type_str = 'I'
    elif data_type in [np.uint32]:
        type_str = 'i'        
    elif data_type in [bool, np.bool_]:
        type_str = 'O'        
    elif data_type in [np.float32]:
        type_str = 'F'
    elif data_type in [np.int8]:
        type_str = 'B'
    elif data_type in [np.uint8]:
        type_str = 'b'
    else:
        raise ValueError('cannot infer leaf type for {}'.format(data_type))
    return type_str

        
        
def fill_branch(tree, values_dict):
    buffer = {}
    leaf_types = {}
    data_sizes = list(set([get_data_size(v) for k,v in values_dict.items()]))
    if len(data_sizes) > 1:
        raise ValueError('cannot fill tree with values of inconsistent entry sizes')
    data_size = data_sizes[0]
    if data_size == 1:
        for k, v in values_dict.items():
            leaf_type_str = get_leaf_type_str(v)
            leaf_types[k] = leaf_type_str
            if leaf_type_str is not None:
                buffer[k] = np.array([v], dtype=type(v))
                tree.Branch(k, buffer[k], '{}/{}'.format(k, leaf_type_str))
            else:
                buffer[k] = ROOT.std.string(v)
                tree.Branch(k, buffer[k])
        tree.Fill()
    else:
        for k, v in values_dict.items():
            leaf_type_str = get_leaf_type_str(v)
            leaf_types[k] = leaf_type_str
            if leaf_type_str is not None:
                buffer[k] = np.array([v[0]], dtype=type(v[0]))
                tree.Branch(k, buffer[k], '{}/{}'.format(k, leaf_type_str))
            else:
                buffer[k] = ROOT.std.string(v[0])
                tree.Branch(k, buffer[k])
        for i in range(data_size):
            for k, v in values_dict.items():
                if leaf_types[k] is not None:
                    buffer[k][0] = v[i]
                else:
                    buffer[k].replace(0, ROOT.std.string.npos, v[i])
            tree.Fill()
            
def close_all_root_files():
    opened_files = ROOT.gROOT.GetListOfFiles()
    for f in opened_files:
        f.Close()
        
def create_declaration(expression:str, name:Optional[str]=None):
    if name is None:
        hash_str = str(hash(expression)).replace("-", "n")
        name_guard = f"__quickstats_declare_{hash_str}__"
    else:
        name_guard = f"__quickstats_declare_{name}__"
    guarded_declaration = f"#ifndef {name_guard}\n"
    guarded_declaration += f"#define {name_guard}\n"
    guarded_declaration += f"\n{expression}\n\n#endif\n"
    return guarded_declaration

def declare_expression(expression:str, name:Optional[str]=None):
    declaration = create_declaration(expression, name)
    status = ROOT.gInterpreter.Declare(declaration)
    return status

def get_tree_names(f:ROOT.TFile):
    tree_names = []
    for i in f.GetListOfKeys():
        obj = f.Get(i.GetName())
        if isinstance(obj, ROOT.TTree):
            tree_names.append(obj.GetName())
    return tree_names

def merge_root_files(source_files:Union[str, List[str]], target_file:str, treename:str=None,
                     multithread:bool=True, keep_order:bool=False, use_template:bool=True,
                     ignore_missing_columns:bool=True, verbosity:str="INFO"):
    from quickstats.utils.io import VerbosePrint
    stdout = VerbosePrint(verbosity)
    
    if isinstance(source_files, str):
        source_files = [source_files]
    rfiles = []
    for source_file in source_files:
        files = glob.glob(source_file)
        if not files:
            raise FileNotFoundError(f"file \"{source_file}\" does not exist")
        rfiles += files
    # now all rfiles are guaranteed to exist
    for i, rfile in enumerate(rfiles):
        stdout.info(f"Source {i+1}: {rfile}")
        if is_corrupt(rfile):
            raise RuntimeError(f"the root file \"{rfile}\" is corrupted")
    if not rfiles:
        raise RuntimeError("no source files found")
    if treename is None:
        f = ROOT.TFile(rfiles[0])
        treenames = get_tree_names(f)
        if len(treenames) > 1:
            raise RuntimeError("unable to deduce tree name from source files: "
                               "multiple trees are present")
        treename = treenames[0]
        stdout.info("INFO: No tree name specified for merging. Will use "
                    f"the auto-detected tree name \"{treename}\".")
        
    # configure multi-threading setting
    multithread_orig_state = ROOT.IsImplicitMTEnabled()
    if multithread and (not multithread_orig_state) and (not keep_order):
        ROOT.EnableImplicitMT()
    if keep_order and multithread_orig_state:
        ROOT.DisableImplicitMT()
    
    if ignore_missing_columns:
        column_map = {}
        all_columns = set()
        for rfile in rfiles:
            rdf = ROOT.RDataFrame(treename, rfile)
            columns = set([str(i) for i in rdf.GetColumnNames()])
            all_columns.update(columns)
            column_map[rfile] = columns
        for fname, columns in column_map.items():
            if columns != all_columns:
                missing_columns = list(all_columns - columns)
                stdout.warning(f"WARNING: The root file \"{rfile}\" is missing the following column(s): "
                               f"{','.join(missing_columns)}. The missing column(s) will not be saved.")
        columns_to_keep = list(set.intersection(*column_map.values()))
        rdf = ROOT.RDataFrame(treename, rfiles)
        stdout.info(f"Target path: {target_file}")
        if use_template:
            snapshot = templated_rdf_snapshot(rdf, columns_to_keep)
        else:
            snapshot = rdf.Snapshot
        snapshot(treename, target_file, columns_to_keep)
    else:
        rdf = ROOT.RDataFrame(treename, rfiles)
        stdout.info(f"Target path: {target_file}")
        if use_template:
            snapshot = templated_rdf_snapshot(rdf, columns_to_keep)
        else:
            snapshot = rdf.Snapshot
        snapshot(treename, target_file)
   
    # restore multi-threading setting
    if multithread_orig_state != ROOT.IsImplicitMTEnabled():
        if multithread_orig_state:
            ROOT.DisableImplicitMT()
        else:
            ROOT.EnableImplicitMT() 