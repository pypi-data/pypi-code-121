"""
Intermediate Representation of AIML.

This module defines the structure of the Abstract Syntax Tree, which
the subsequent submodules work with, and parsed .aiml files are converted to.

The exported names are:
    ``Node`` - represents a part (subtree) of XML
    ``Category`` - basic knowledge of AIML chatbot
"""

from .node import Node
from .category import Category


__all__ = ["Node", "Category"]
