"""  Utils for Dicts in order to process them and use their information for the function that allows to
   download the displayed data in a document on the tree
"""
import logging

logger = logging.getLogger(__name__)


def get_values_items(dict_structure, values):
    """Get all values from an inclusion of dictionaries

    Args:
        dict_structure: inclusion of dictionnary
        values: list[tag,value]

    Returns:
        list
    """
    for element in dict_structure:
        if element is dict or isinstance(element, dict):
            list_items_values = []
            for key in element:
                if "item" in str(key):  # We have an inclusion of dict
                    get_values_items(element[key], list_items_values)
                else:  # We have a simple dict
                    list_items_values.append(str(element[key]))
            values.append(list_items_values)

    return values


def check_empty_nodes(xml):
    """Check if there are empty leafs in an XML tree (all child where child.text="")

    Args:
        xml:

    Returns:
        Boolean
    """
    for child in xml.getiterator():
        # Fixme if len(child.getchildren()==0
        if child.getchildren():
            logger.info("check_empty_nodes no children")
        else:
            if child.text == "":
                return True
    return False


def remove_empty_nodes(xml):
    """Remove empty leafs of the tree (all child where child.text="")

    Args:
        xml:

    Returns:

    """
    for child in xml.getiterator():
        # Fixme if len(child.getchildren()==0
        if child.getchildren():
            pass
        else:
            if child.text == "":
                try:
                    parent = child.findall("..")
                    parent[0].remove(child)
                except Exception as e:
                    logger.warning(
                        "remove_empty_nodes threw an exception: {0}".format(str(e))
                    )
