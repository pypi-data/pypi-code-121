"""
- Authors: Peter Mawhorter
- Consulted:
- Date: 2022-3-3
- Purpose: Main file where the top-level commands live.

This file includes the following key functions:

- `readJournal`: This function accepts a string containing journal
    information, and returns a list of exploration graphs, each
    representing a subsequent step recorded by the journal.
"""

from . import journal
from . import core

def readJournal(journal: str) -> core.Exploration:
    """
    """
