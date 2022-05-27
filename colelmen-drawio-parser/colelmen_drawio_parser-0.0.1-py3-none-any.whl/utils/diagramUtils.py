# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long



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



def get_connectors(element):
    return element.xpath("mxCell[@target]")

def get_children(element):
    if isinstance(element,(list)):
        element = element[0]
    children = element.xpath("*")
    return children
    # print(f"children: {children}")

def get_diagram_root_node(element):
    mxGraphModel = element.xpath('mxGraphModel')
    root = mxGraphModel[0].xpath('root')
    return root

def get_nodes(element):
    return element.xpath("mxCell")

def attrib_to_dict(attrib):
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