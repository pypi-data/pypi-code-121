"""
Seeders are classes to feed Pipeline
"""

from .csvseeder import CsvSeeder
from .jsonseeder import JsonSeeder

__all__ = ["CsvSeeder", "JsonSeeder"]
