from os.path import dirname, basename, isfile, join, abspath
from importlib import import_module
import sys
import glob
from functools import reduce
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import debugValues, logShouldRun
from .. import MODEL as PARENT_MODEL

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
MODEL = 'dataCompleteness'
PKG = '.'.join(['hestia_earth', 'models', PARENT_MODEL, MODEL])
modules = glob.glob(join(dirname(__file__), '*.py'))
modules = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
MODELS = list(map(lambda m: {'key': m, 'run': getattr(import_module(f".{m}", package=PKG), 'run')}, modules))


def _should_run_model(model, cycle: dict):
    is_complete = cycle.get('dataCompleteness', {}).get(model.get('key'))
    should_run = is_complete is False
    logShouldRun(MODEL, None, should_run, key=model.get('key'))
    return should_run


def _run_model(model, cycle: dict):
    return {model.get('key'): model.get('run')(cycle)} if _should_run_model(model, cycle) else None


def _run(cycle: dict):
    values = non_empty_list([_run_model(model, cycle) for model in MODELS])
    value = reduce(lambda prev, curr: {**prev, **curr}, values, cycle.get('dataCompleteness', {}))
    keys = ','.join([next(iter(val)) for val in values])
    debugValues(model=MODEL, keys=keys)
    return value if len(values) > 0 else None


def run(cycle: dict): return _run(cycle)
