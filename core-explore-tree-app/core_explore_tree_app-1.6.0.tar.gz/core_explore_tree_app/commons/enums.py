""" Enums file
"""
from enum import Enum


class QueryOntologyStatus(Enum):
    uploaded = 0
    active = 1
    blank = 2
    disabled = -1
