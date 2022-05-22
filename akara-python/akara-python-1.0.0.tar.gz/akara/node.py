from typing import List


class Node:
    def __init__(self, word: str, children, parent=None) -> None:
        self.word = word
        self.parent = parent
        self.children = children

    def same_weight_child(self, weight: int):
        try:
            return self.children[[w for (w, node) in self.children].index(weight)][1]
        except:
            return None
