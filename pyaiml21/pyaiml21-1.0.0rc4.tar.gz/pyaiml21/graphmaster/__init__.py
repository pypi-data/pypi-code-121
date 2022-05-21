"""
Implementation of the graphmaster.

The :mod:`pyaiml21.graphmaster` module contains implementation of
the graphmaster - the main data structure used in the AIML interpreter for
saving the categories and finding the best category for the given user input
using pattern matching.
"""
from .graphmaster import GraphMaster
from .mongo_gm import MongoGraphMaster
from .sqlite_gm import SqLiteGraphMaster
from .pattern import Pattern, MatchFn
from .node import GMNode
from .stars import StarBindings


__all__ = [
    "GraphMaster", "MatchFn",
    "MongoGraphMaster",
    "SqLiteGraphMaster",
    "GMNode",
    "Pattern",
    "StarBindings"
]
