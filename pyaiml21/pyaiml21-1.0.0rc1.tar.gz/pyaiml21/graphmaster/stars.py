"""
Storage for matched parts of user's input.

The graphmaster enables using regular-expression-like constructs
to match user input. The matches are, by the standard, called stars.

Each star represents a substring of pattern path, that was matched
with some of the constructs mentioned above.
"""
from typing import List
from dataclasses import dataclass, field


@dataclass
class StarBindings:
    """
    Wildcard-matched parts of the user's input.

    Storage for matched stars as they were discovered while matching
    the graphmaster with the user's input.
    """

    stars: List[str] = field(default_factory=list)
    """stars found in the last user query"""
    thatstars: List[str] = field(default_factory=list)
    """stars from the last bots answer, aka that / context"""
    topicstars: List[str] = field(default_factory=list)
    """stars matched with current conversational topic"""
