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

    def children_in_tolerance(self, lower: int, upper: int) -> List:
        return [child[1] for child in self.children if child[0] >= lower and child[0] <= upper]
