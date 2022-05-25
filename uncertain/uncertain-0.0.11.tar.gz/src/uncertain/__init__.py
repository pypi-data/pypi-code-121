""" Uncertain numbers: probability distributions, uncertainty propagation and more.

.. module:: uncertain
.. moduleauthor:: Miguel Nuño <mnunos@outlook.com>

"""
# flake8: noqa
from .uncertain import UncertainValue, probability_in_interval, from_data

__all__ = ['UncertainValue', 'probability_in_interval', 'from_data']

__version__ = "0.0.11"
