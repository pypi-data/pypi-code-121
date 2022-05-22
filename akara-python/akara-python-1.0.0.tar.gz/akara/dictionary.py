from typing import List
import xml.etree.cElementTree as ET

from .node import Node
from .edit_distance import edit_distance


class Dictionary:
    def __init__(self, dict_path: str) -> None:
        """ Initializes the Dictionary class.
        Args
        ---
        - `dict_path`: Path to the dictionary file.
        """
        self.words = self.__read_words(dict_path)

    def save(self, output_filepath: str) -> None:
        """ Save the BK-tree to an xml file at `output_filepath`.

        Args
        ---
        - `output_filepath`: The location to save the output xml file.
        """
        print("-- building bk-tree")
        root = self.__build_bk_tree()

        print("-- writing tree to xml file.")
        xml_root = ET.Element("root")
        xml_tree = ET.ElementTree(xml_root)

        queue = [(0, root)]

        while len(queue) != 0:
            (w, curr_node) = queue.pop(0)

            if curr_node.parent is None:
                parent_node_xml = xml_root
            else:
                parent_node_xml = xml_root.find(f".//node[@word='{curr_node.parent.word}']")
                parent_node_xml = parent_node_xml.find("children")

            curr_node_xml = ET.Element("node", word=curr_node.word, weight=str(w))
            curr_node_node_children_xml = ET.Element("children")
            curr_node_xml.append(curr_node_node_children_xml)

            for child in curr_node.children:
                queue.append(child)

            parent_node_xml.append(curr_node_xml)

        xml_tree.write(output_filepath, encoding="UTF-8")

    def __build_bk_tree(self) -> Node:
        root = Node(self.words[0], parent=None, children=[])
        for word_idx in range(1, len(self.words)):
            current_word = self.words[word_idx]
            self.__insert(root, current_word)

        return root

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

    def __read_words(self, path: str) -> List[str]:
        with open(path, "r") as dict_file:
            return [word.strip("\n") for word in dict_file.readlines()]
