import os
from typing import List
import xml.etree.cElementTree as ET

from .node import Node
from .edit_distance import edit_distance


class SpellChecker:
    """ The spell check uses the popular combination of Levenstein Distance (Edit Distance) and the BK-Tree to quickly search for correct word suggestions. """

    def __init__(self, model_path: str = None) -> None:
        if model_path is None:
            model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "model.xml")

        self.root = ET.parse(model_path).getroot().getchildren()[0]

    def suggest(self, word: str, num_suggestions: int = 3, N: int = 2) -> List[str]:
        """ Suggests a list of corrections for `word`.

        Args
        ---
        - `word`: The word to get suggestions for.
        - `num_suggestions`: The number of suggestions to return.

        Returns
        ---
        A list of suggested corrections.
        """
        matches = []

        stack: List[ET.Element] = [self.root]

        while len(stack) != 0:
            curr_node = stack.pop()
            curr_node_word = curr_node.attrib["word"]
            distance_curr_node = edit_distance(word, curr_node.attrib["word"])
            if distance_curr_node <= N and (curr_node_word, distance_curr_node) not in matches:
                matches.append((curr_node_word, distance_curr_node))

            for child in curr_node.find("children").getchildren():
                child_weight = int(child.attrib["weight"])
                if child_weight >= (distance_curr_node - N) and child_weight <= (distance_curr_node + N):
                    stack.append(child)

        return [match[0] for match in sorted(matches, key=lambda x: x[1])][:num_suggestions]
