"""Module that will help with virtual environments so it's possible to work with venv from python.
You can create, delete or update dependencies."""

from mypythontools_cicd.venvs.venvs_internal import Venv, is_venv, prepare_venvs

__all__ = ["Venv", "is_venv", "prepare_venvs"]
