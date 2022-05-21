"""The basic unit of knowledge of an AIML chatbot."""
from dataclasses import dataclass
from typing import Optional
from .node import Node


@dataclass
class Category:
    """
    Category represents a basic knowledge of an AIML chatbot.

    A category consists of pattern, that and topic that constitute a pattern
    path for matching in the graphmaster, and a template that contains
    instructions to calculate the response for user's input.
    """

    pattern: Node
    template: Node
    that: Optional[Node] = None
    topic: Optional[Node] = None

    def __str__(self) -> str:
        """Return string representation of the category."""
        return (
            f"Category:\n"
            f"==========\n"
            f"{self.pattern}\n"
            f"{self.that}\n"
            f"{self.topic}\n"
            f"{self.template}"
        )
