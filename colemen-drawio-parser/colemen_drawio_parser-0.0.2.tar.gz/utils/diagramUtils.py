# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
from typing import Iterable,TypeVar
from diagram import Diagram
from lxml import etree
element_type = TypeVar('element_type', bound=etree.Element)



def get_by_attribute(tree,values,attribute,element=None):
    if isinstance(values,(list)) is False:
        values = [values]
    elements = []
    for v in values:
        r = []
        if element is None:
            r = tree.xpath(f"//*[contains(@{attribute},'{v}')]")
        if element is not None:
            r = tree.xpath(f"//{element}[contains(@{attribute},'{v}')]")
        if len(r) > 0:
            elements = elements + r
    return elements

def get_by_label(tree,labels,element=None):
    if isinstance(labels,(list)) is False:
        labels = [labels]
    elements = []
    for l in labels:
        r = []
        if element is None:
            r = tree.xpath(f"//*[contains(@label,'{l}')]")
            # r = tree.xpath(f"//attribute::*[contains(., '{t}')]")
        if element is not None:
            r = tree.xpath(f"//{element}[contains(@label,'{l}')]")
        if len(r) > 0:
            elements = elements + r
    return elements


def get_diagrams(tree):
    result = []
    diagrams = tree.xpath("//diagram['@name']")
    if len(diagrams) > 0:
        for d in diagrams:
            result.append(Diagram(tree,d))
    return result



def get_connectors(element):
    return element.xpath("mxCell[@target]")

def get_children(element:element_type)->Iterable[element_type]:
    '''
        Get all direct children of the element provided.

        ----------

        Arguments
        -------------------------
        `element` {any}
            The parent element to search within.

        Return {list}
        ----------------------
        A list of children elements

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 05-27-2022 13:15:21
        `memberOf`: diagramUtils
        `version`: 1.0
        `method_name`: get_children
    '''


    if isinstance(element,(list)):
        element = element[0]
    children = element.xpath("*")
    return children

def get_diagram_root_node(element:element_type)->element_type:
    '''
        Retrieves the diagrams literal "root" element

        ----------

        Arguments
        -------------------------
        `element` {any}
            The diagram element to search within.

        Return {any}
        ----------------------
        The root element if it is found, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 05-27-2022 13:17:44
        `memberOf`: diagramUtils
        `version`: 1.0
        `method_name`: get_diagram_root_node
    '''

    root = False
    mx_graph_model = element.xpath('mxGraphModel')
    if len(mx_graph_model) > 0:
        root = mx_graph_model[0].xpath('root')
    return root

def get_nodes(element):
    return element.xpath("mxCell")

def attrib_to_dict(attrib)->dict:
    '''
        Convert a nodes attributes to a dictionary.

        ----------

        Arguments
        -------------------------
        `attrib` {dict}
            The lxml attribute dictionary.

        Return {dict}
        ----------------------
        The attribute dictionary.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 05-27-2022 13:27:45
        `memberOf`: diagramUtils
        `version`: 1.0
        `method_name`: attrib_to_dict
    '''

    
    data = {}
    for k,v in attrib.items():
        data[k] = v
    return data


def style_to_dict(style):
    data = {}
    if isinstance(style,(str)):
        styleList = style.split(";")
        for x in styleList:
            s = x.split("=")
            if len(s) > 1:
                # print(f"s: {s}")
                data[s[0]] = s[1]
    return data