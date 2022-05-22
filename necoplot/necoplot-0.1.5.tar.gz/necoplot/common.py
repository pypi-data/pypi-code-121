import inspect
import itertools
from typing import Callable, Optional, Union

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes._axes import Axes

import necoplot.config as config
import necoplot.extract_params as extract_params


FIGURE_PARAMS = extract_params.FIGURE_PARAMS
AXES_PARAMS = extract_params.AXES_PARAMS


def _apply_user_parameters(target_kwargs:list[Union[str, list]]):
    """Decorator to apply user parameters to a target function"""
    
    if isinstance(target_kwargs[0], list):
        target_kwargs = list(itertools.chain.from_iterable(target_kwargs))
    
    def _apply_config(func):
        
        def wrapper(*args, **kwargs):
            
            parameter = {key:value for key, value in config.user_parameters.items() if key in target_kwargs}
            kwargs = {**parameter, **kwargs}
            
            result = func(*args, **kwargs)
            
            return result
        
        return wrapper
    
    return _apply_config


@_apply_user_parameters(AXES_PARAMS)
def config_ax(index: int = 111,
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
    xlim: tuple[float, float] = None,
    ylim: tuple[float, float] = None,
    xticks: list = None,
    yticks: list = None,
    xticklabels: str = None,
    yticklabels: str = None,
    **kwargs) -> Callable:
    """Return a function to config ax with keyword args"""
    
    kwargs_not_packed = _get_local_kwargs(exception=['index'])
    all_kwargs = {**kwargs_not_packed, **kwargs}
    
    def _config_ax(fig):
        
        ax = fig.add_subplot(index, **all_kwargs)
        
        return ax

    return _config_ax


def _get_local_kwargs(exception: Optional[list[str]]=None) -> dict:
    """Return parent function args and values as dict"""
    
    exception = exception if exception else []
    exception = exception + ['args', 'kwargs']
    
    fname = inspect.currentframe().f_back
    args_dict = inspect.getargvalues(fname).locals
        
    args_dict = {k: v for k, v in args_dict.items() if k not in exception}
    args_dict = {k: v for k, v in args_dict.items() if v is not None}
    
    return args_dict


def save(fname: str, show=True, **kwargs) -> None:
    """Save a figure with keyword args"""
    plt.savefig(fname, **kwargs)
    plt.close() if not show else None
    

def config_user_parameters(**kwargs):
    """Set parameters(like default values of args) as you like"""
    config.user_parameters.update(kwargs)
    

def reset():
    """Reset user parameters"""
    config.user_parameters = {}