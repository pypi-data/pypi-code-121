from os.path import dirname, abspath
import sys
from importlib import import_module

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)
MODEL = 'pribyl2010'
PKG = '.'.join(['hestia_earth', 'models', MODEL])


def run(model: str, data):
    model_name = model or '_all'
    module = import_module(f".{model_name}", package=PKG)
    run = getattr(module, 'run')
    return run(data)
