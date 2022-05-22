from typing import Optional, Union, Dict, List
import os
import sys
import copy
import fnmatch
import time
import json
import inspect
import datetime
import functools
import collections.abc

import numpy as np

def timely_info(green_text, normal_text, adjust=40):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '\033[92m[INFO]\033[0m', '\033[92m{}\033[0m'.format(green_text).rjust(40, ' '), normal_text)

def get_cpu_count():
    return os.cpu_count()

def parallel_run(func, *iterables, max_workers):
    from concurrent.futures  import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers) as executor:
        result = executor.map(func, *iterables)

    return [i for i in result]

def execute_multi_tasks(func, *iterables, parallel):
    if parallel == 0:
        result = []
        for args in zip(*iterables):
            result.append(func(*args))
        return result
    else:
        if parallel == -1:
            max_workers = get_cpu_count()
        else:
            max_workers = parallel
        return parallel_run(func, *iterables, max_workers=max_workers)


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print('INFO: All jobs have finished. Total time taken: {:.3f} s'.format(run_time))
        return value
    return wrapper_timer

def stdout_print(msg):
    sys.__stdout__.write(msg + '\n')
    
def redirect_stdout(logfile_path):
    import ROOT
    sys.stdout = open(logfile_path, 'w')
    ROOT.gSystem.RedirectOutput(logfile_path)

def restore_stdout():
    import ROOT
    if sys.stdout != sys.__stdout__:
        sys.stdout.close()
    sys.stdout = sys.__stdout__
    ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')

def redirect_stdout_test(func):
    """Redirect stdout to a log file"""
    import ROOT
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        logfile_path = kwargs.get('logfile_path', None)
        if logfile_path is not None:
            sys.stdout = open(logfile_path, 'w')
            ROOT.gSystem.RedirectOutput(logfile_path)
            value = func(*args, **kwargs)
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')
            return value
        else:
            return func(*args, **kwargs)
    return wrapper_timer

def json_load(fp, *args, **kwargs):
    try:
        data = json.load(fp, *args, **kwargs)
    except:
        raise RuntimeError(f"broken json input: {fp}")
    return data


def parse_config(source:Optional[Union[Dict, str]]=None):
    if source is None:
        return {}
    elif isinstance(source, str):
        with open(source, 'r') as f:
                config = json.load(f)
        return config
    elif isinstance(source, dict):
        return source
    else:
        raise ValueError("invalid config input")
        
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    
def update_nested_dict(d:Dict, u:Dict):
    for k, v in u.items():
        if isinstance(d.get(k, None), collections.Mapping) and isinstance(v, collections.Mapping):
            d[k] = update_nested_dict(d[k], v)
        else:
            d[k] = v
    return d

def combine_dict(d:Dict, u:Optional[Dict]=None):
    d_copy = copy.deepcopy(d)
    if u is None:
        return d_copy
    else:
        u_copy = copy.deepcopy(u)
        return update_nested_dict(d_copy, u_copy)
    
def str_list_filter(source:List[str], patterns:List[str], inclusive:bool=True):
    if inclusive:
        result = [s for p in patterns for s in source if fnmatch.fnmatch(s, p)]
        return sorted(list(set(result)))
    else:
        result = set(source)
        for p in patterns:
            result &= set([s for s in source if not fnmatch.fnmatch(s, p)])
        return sorted(list(result))

def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)

def batch_makedirs(dirnames:Union[str, List[str], Dict[str, str]]):
    if isinstance(dirnames, str):
        batch_makedirs([dirnames])
    elif isinstance(dirnames, list):
        for dirname in dirnames:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
    elif isinstance(dirnames, dict):
        for key in dirnames:
            if not os.path.exists(dirnames[key]):
                os.makedirs(dirnames[key])

def set_scripts_path(scripts_path, undo=False):
    if (scripts_path in sys.path) and (undo==True):
        sys.path.remove(scripts_path)
        os.environ["PYTHONPATH"].replace(scripts_path+":","")
        
    if (scripts_path not in sys.path) and (undo==False):
        sys.path.insert(0, scripts_path)
        os.environ["PYTHONPATH"] = scripts_path + ":" + os.environ.get("PYTHONPATH", "")
        
def is_valid_file(fname:str):
    if not os.path.exists(fname):
        return False
    ext = os.path.splitext(fname)[-1]
    if ext == ".root":
        from quickstats.utils.root_utils import is_corrupt
        return not is_corrupt(fname)
    return (os.path.isfile(fname)) and (os.path.getsize(fname) > 0)

def remove_list_duplicates(seq:List, keep_order:bool=True):
    if keep_order:
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]
    else:
        return list(set(seq))
    
def format_delimiter_enclosed_text(text:str, delimiter:str, width:int=10):
    full_line_width = 2 * width + ( len(text) if (len(text) > 2 * width) else (2 * width) ) + 2
    full_line = delimiter * full_line_width
    line = delimiter * width
    result = f"\n\t {full_line}\n"
    if len(text) > 2 * width:
        result += f"\t {line} {text} {line}\n"
    else:
        result += f"\t {line}{text.center(2*width+2)}{line}\n"
    result += f"\t {full_line}\n"
    return result
        

def filter_by_wildcards(targets:List, conditions:Optional[Union[str, List]]=None, exclusion:bool=False):
    if not conditions:
        return targets
    selected = []
    if isinstance(conditions, str):
        conditions = [i.strip() for i in conditions.split(",")]
    for target in targets:
        if any([fnmatch.fnmatch(target, condition) for condition in conditions]):
            selected.append(target)
    if exclusion:
        return [target for target in targets if target not in selected]
    return selected