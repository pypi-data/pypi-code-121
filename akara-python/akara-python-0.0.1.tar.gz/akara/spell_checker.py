import os
from typing import List
from .node import Node
from .edit_distance import edit_distance


class SpellChecker:
    """ The spell check uses the popular combination of Levenstein Distance (Edit Distance) and the BK-Tree to quickly search for correct word suggestions. """

    def __init__(self) -> None:
        """ Initializes the spell checker. """
        self.words = self.__read_words("dict.txt")
        assert len(self.words) > 0, "words cannot be empty."
        self.root = self.__build_bk_tree()

    def is_correct(self, word: str) -> bool:
        """ Check whether `word` is misspelled. `word` is misspelled when it does not exist in the dictionary.

        Args
        ---
        - `word`: the word to check.

        Returns
        ---
        A boolean indicating whether `word` is correct.
        """
        return word in self.words

    def suggest(self, word: str, num_suggestions: int = 3) -> List[str]:
        """ Suggests a list of corrections for `word`.

        Args
        ---
        - `word`: The word to get suggestions for.
        - `num_suggestions`: The number of suggestions to return.

        Returns
        ---
        A list of suggested corrections.
        """
        return self.__search(word)[:num_suggestions]

    def __search(self, word: str, N: int = 2) -> List[str]:
        """ Search the BK-Tree using depth-first search. """
        matches = []

        stack: List[Node] = [self.root]

        while len(stack) != 0:
            curr_node = stack.pop()
            distance_curr_node = edit_distance(word, curr_node.word)
            if distance_curr_node <= N and (curr_node.word, distance_curr_node) not in matches:
                matches.append((curr_node.word, distance_curr_node))

            children = curr_node.children_in_tolerance(
                lower=distance_curr_node-N,
                upper=distance_curr_node+N
            )

            stack += children

        return [match[0] for match in sorted(matches, key=lambda x: x[1])]

    def __insert(self, root: Node, word: str):
        curr_node = root
        inserted = False

        while not inserted:
            dist_curr_node = edit_distance(word, curr_node.word)
            same_weight_child = curr_node.same_weight_child(dist_curr_node)
            if same_weight_child is not None:
                curr_node = same_weight_child
            else:
                if curr_node.word != word:
                    new_node = Node(word, parent=curr_node, children=[])
                    curr_node.children.append((dist_curr_node, new_node))

                inserted = True

    def __build_bk_tree(self) -> Node:
        root = Node(self.words[0], parent=None, children=[])
        for word_idx in range(1, len(self.words)):
            current_word = self.words[word_idx]
            self.__insert(root, current_word)

        return root

    def __read_words(self, filename: str) -> List[str]:
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        asset_folder = os.path.join(parent_dir, "assets")
        path = os.path.join(asset_folder, filename)

        with open(path, "r") as dict_file:
            return [word.strip("\n") for word in dict_file.readlines()]
