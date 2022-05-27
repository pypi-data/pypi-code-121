
import colemen_file_utils as cfu
# import colemen_string_utils as csu
from lxml import etree
import json
import objectUtils as obj
from io import StringIO, BytesIO


# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring


class NodeBase:
    def __init__(self,tree,element=None,diagram=None):
        self.settings = {}
        self.tree = tree
        self.diagram = diagram
        self.element = element
        self.data = {
            "attributes":{}
        }

    def to_element(self,to_string=False):
        self.xml()
        if to_string:
            return self.data['xml']
        return self.data['lxml']

    def xml(self):
        root_obj = etree.Element("object")
        for k,v in self.data['attributes'].items():
            if k == "tags":
                root_obj.attrib[k] = ",".join(v)
            else:
                root_obj.attrib[k] = v


        mxcell = etree.SubElement(root_obj, 'mxCell')
        for k,v in self.data['mxcell']['attributes'].items():
            if k == 'style':
                mxcell.attrib[k] = style_to_string(v)
            else:
                mxcell.attrib[k] = v

        mxgeo = etree.SubElement(mxcell, 'mxGeometry')
        for k,v in self.data['mxcell']['mxgeometry'].items():
            mxgeo.attrib[k] = v


        # print(etree.tostring(root_obj))
        self.data['lxml'] = root_obj
        self.data['xml'] = etree.tostring(root_obj)
        return self.data['xml']

    def set_attribute(self,attribute,value):
        self.data['attributes'][attribute] = value
        self.element.attrib[attribute] = self.data['attributes'][attribute]

    def remove_attribute(self,attribute):
        new_attrib = {}
        for k,v in self.data['attributes'].items():
            if k != attribute:
                new_attrib[k] = v

        self.data['attributes'] = new_attrib

    def has_attribute(self,attribute):
        if attribute in self.data['attributes']:
            return True
        return False

    def set_dict_style(self,styles):
        for k,v in styles.items():
            self.set_style(k,v)
        
            

    def set_style(self,key,value):
        # print(f"self.data['mxcell']['style']: {self.data['mxcell']['style']}")
        style = self.data['mxcell']['attributes']['style']
        style[key] = value
        self.data['mxcell']['attributes']['style'] = style
        mxCell = self.element.xpath('mxCell')
        # print(f"self.data['mxcell']['style']: {self.data['mxcell']['style']}")
        mxCell[0].attrib['style'] = style_to_string(style)

    def remove_style(self,key):
        new = {}
        for k,v in self.data['mxcell']['style'].items():
            if k != key:
                new[k] = v

        self.data['mxcell']['style'] = new
        mxCell = self.element.xpath('mxCell')
        mxCell[0].attrib['style'] = style_to_string(self.data['mxcell']['style'])

    def get_id(self):
        return self.data['attributes']['id']

    def has_id(self,value):
        if 'id' in self.data['attributes']:
            if self.data['attributes']['id'] == value:
                return True
        return False

    def get_source(self,default_val=''):
        if 'source' in self.data['attributes']:
            return self.data['attributes']['source']
        return default_val

    def get_target(self,default_val=''):
        if 'target' in self.data['attributes']:
            return self.data['attributes']['target']
        return default_val

    def get_label(self,default_val=''):
        if 'label' in self.data['attributes']:
            return self.data['attributes']['label']
        return default_val

    def set_label(self,value):
        self.data['attributes']['value'] = value
        self.data['attributes']['label'] = value
        self.set_attribute("label",value)
        self.set_attribute("value",value)

    def has_label(self,value,default_val=None):
        if 'label' in self.data['attributes']:
            if self.data['attributes']['label'] == value:
                return True

        return default_val

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

def style_to_string(style):
    tmp = []
    if isinstance(style,(dict)):
        for k,v in style.items():
            tmp.append(f"{k}={v}")
    return ';'.join(tmp)

def attrib_to_dict(attrib):
    data = {}
    for k,v in attrib.items():
        data[k] = v
    return data


