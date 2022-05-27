""" Node Class that represents a structure from a query and its value
"""

import logging
from builtins import next, zip, object
from itertools import tee

logger = logging.getLogger(__name__)


class QueryNode(object):
    """QueryNode class"""

    def __init__(self, data, text=""):
        self.data = data
        self.text = text
        self.children = []

    def add_child(self, obj):
        """Add a child to the Node

        Args:
            obj:

        Returns:

        """
        self.children.append(obj)

    def get_child(self, data):
        """Get the child of the Node

        Args:
            data:

        Returns:

        """
        for child in self.children:
            if data == child.data:
                return child
        return None

    def set_texts(self, list_of_texts):
        """Set all values of the leafs for a QueryNode structure

        Args:
            list_of_texts:

        Returns:

        """
        i = 0
        for child in self.getiterator():
            # Fixme if len(child.getchildren()==0
            if child.getchildren():
                logger.info("set_texts no children")
            else:
                child.text = list_of_texts[i]
                i += 1


def aggregate_query(query_list, query_result_list):
    """Re build the xml from parts of xml coming from a same document

    Args:
        query_list: list of query path. eg: query_list = ["a.b.c.d","a.b.c.e","a.b.f.g"]
        query_result_list:

    Return:
        Node
    """
    # Check that the first element of each query are all identical and we initialize the root
    queries = [query.split(".") for query in query_list]
    if not queries or [_[0] for _ in queries].count(queries[0][0]) == len(queries):
        # Initialize the root of Node structure (Root of the xml)
        root = QueryNode(queries[0][0], text="")
        # Create a QueryNode tree (eq xml)
        # eg: query_list = ["a.b.c.d","a.b.c.e","a.b.f.g"]
        # Create the Node:      a
        #                       b
        #                    c     f
        #                   d e    g
        for query, value in zip(queries, query_result_list):
            current_node = root
            for element in query[1:]:
                child = current_node.get_child(element)
                # Add the text if we have a leaf
                if child is None:
                    new_node = QueryNode(
                        element, text=value if element == query[-1] else ""
                    )
                    current_node.add_child(new_node)
                    current_node = new_node
                else:
                    current_node = child
        return root
    else:
        print("No common root")


def tree_to_xml_string(tree):
    """Conversion of an Node-Tree into an XML String

    Args:
        tree:
            Node tree
    Return:
        XML String
    """

    xml_string = rec_xml_to_string(tree)
    # Post cleaning of the string
    # Removing useless characters and empty tags
    xml_str_split = xml_string.split("><")
    xml_str_split[0] = xml_str_split[0][1:]
    xml_str_split[-1] = xml_str_split[-1][:-1]
    # Finding duplicated tags and filtering them
    remove_idx = [
        i
        for i, (a, b) in enumerate(iter_2_by_2(xml_str_split))
        if (a.startswith("/") and a[1:] == b)
    ]
    remove_idx_set = set(remove_idx) | set([x + 1 for x in remove_idx])
    filtered_list = [
        "<{}>".format(x)
        for i, x in enumerate(xml_str_split)
        if (i not in remove_idx_set)
    ]
    return "<data>{}".format("".join(filtered_list))


def iter_2_by_2(iterable):
    """Get list of following Nodes

    Args:
        iterable:

    Returns:

    """
    # for a s -> (s0,s1), (s1,s2), (s2, s3)
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def rec_xml_to_string(tree):
    """Function that builds XML tags through a depth-first search. Returns: string containing tags around each nodes


    Args:
        tree:

    Returns:

    """
    current_node = tree
    left = "<{}>".format(current_node.data)
    right = "</{}>".format(current_node.data)
    if current_node.children:
        return "".join(
            [left + rec_xml_to_string(child) + right for child in current_node.children]
        )
    else:  # it is a leaf
        return left + current_node.text + right
