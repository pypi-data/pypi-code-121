import inspect

from matplotlib.figure import Figure
from matplotlib.axes._axes import Axes

def extract_params(target_class: object):
    """Extract parameters including **kwargs parameters"""
    
    params = list(inspect.signature(target_class).parameters.keys())
    
    all_members = [m for m in dir(target_class) if not m.startswith('_')]
    
    func_members = [m[0] for m in inspect.getmembers(target_class, inspect.isfunction)]
    func_members = [m for m in func_members if not m.startswith('set_')]
    
    param_members = [m.replace('set_', '') for m in all_members if m not in func_members]
    
    params = params + param_members
    
    return params

FIGURE_PARAMS = extract_params(Figure)
AXES_PARAMS = extract_params(Axes)