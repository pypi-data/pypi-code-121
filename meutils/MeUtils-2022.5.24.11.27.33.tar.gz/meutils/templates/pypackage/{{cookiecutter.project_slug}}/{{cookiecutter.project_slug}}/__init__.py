"""Top-level package for {{ cookiecutter.project_name }}."""
import time

__author__ = """{{ cookiecutter.full_name }}"""
__email__ = '{{ cookiecutter.email }}'
# __version__ = '{{ cookiecutter.version }}'
__version__ = time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime())
