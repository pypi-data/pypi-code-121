"""Strangeworks Rigetti SDK"""
import importlib.metadata
from .strange import get_qc, list_quantum_computers, fetch_job

__version__ = importlib.metadata.version("strangeworks-rigetti")

list_quantum_computers = list_quantum_computers
get_qc = get_qc
fetch_job = fetch_job
