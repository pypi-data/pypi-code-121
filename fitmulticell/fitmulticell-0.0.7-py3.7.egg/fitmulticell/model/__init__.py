"""
Model
=====

Models wrap around a simulation engine (such as Morpheus) and
making their results accessible to the parameter inference
routine (such as pyABC).
"""

from .base import MorpheusModel, MorpheusModels
