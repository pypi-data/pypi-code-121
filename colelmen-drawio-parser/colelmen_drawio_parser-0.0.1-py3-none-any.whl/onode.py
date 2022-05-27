
# import colemen_file_utils as cfu
import colemen_string_utils as csu
from lxml import etree
# import json
# import objectUtils as obj
from nodeBase import NodeBase
import utils.diagramUtils as dia
# from io import StringIO, BytesIO


# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
def new_onode(tree,diagram,id=None):
    o = etree.SubElement(diagram.dia_root, 'object')
    id = csu.gen.rand() if id is None else id
    o.attrib['id'] = id

    mxCell = etree.SubElement(o, 'mxCell')
    # mxCell.attrib['style']="shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;size=10;fillColor=#76608a;strokeColor=#432D57;fontColor=#ffffff;"
    mxCell.attrib['style']="rounded=0;whiteSpace=wrap;html=1;"
    mxCell.attrib['vertex']="1"
    mxCell.attrib['parent']="1"

    mxGeo = etree.SubElement(mxCell, 'mxGeometry')
    mxGeo.attrib['x']="0"
    mxGeo.attrib['y']="0"
    mxGeo.attrib['width']="120"
    mxGeo.attrib['height']="60"
    mxGeo.attrib['as']="geometry"

    return Onode(tree,o,diagram)

class Onode(NodeBase):
    def __init__(self,tree,element=None,diagram=None):
        super().__init__(tree,element,diagram)
        self.settings = {}
        self.tree = tree
        self.element = element
        self.data = {
            "node_type":"onode",
            "lxml":"",
            "xml":"",
            "coords":{
                "x":None,
                "y":None,
                "tlc":[],
                "trc":[],
                "brc":[],
                "blc":[],
            },
            "attributes":{},
            "mxcell":{
                "style":{},
                "vertex":None,
                "parent":None,
                "mxgeometry":{
                    "x":None,
                    "y":None,
                    "width":None,
                    "height":None,
                    "as":None,
                },
            },
        }
        self._from_element()
        # self.set_defaults()



    def _from_element(self):
        element = self.element
        if element is not None:
            self.data['attributes'] = dia.attrib_to_dict(element.attrib)
            if 'tags' in self.data['attributes']:
                self.data['attributes']['tags'] = self.data['attributes']['tags'].split(",")

            # @Mstep [] parse the mxcell attributes
            mxcell = element.xpath('mxCell')
            self.data['mxcell']['attributes'] = dia.attrib_to_dict(mxcell[0].attrib)
            # style = dia.style_to_dict(self.data['mxcell']['attributes']['style'])
            # print(f"style:{style}")

            # @Mstep [] retrieve and parse the mxGeometry attributes.
            mxgeometry = mxcell[0].xpath('mxGeometry')
            self.data['mxcell']['mxgeometry'] = dia.attrib_to_dict(mxgeometry[0].attrib)

            self.data['mxcell']['attributes']['style'] = dia.style_to_dict(self.data['mxcell']['attributes']['style'])


            return self.data

    def set_coords(self,x=None,y=None,w=None,h=None):
        if self.data['coords']['x'] is None:
            self.coords()

        if x is None:
            x = self.data['mxcell']['mxgeometry']['x']
        if y is None:
            y = self.data['mxcell']['mxgeometry']['y']
        if w is None:
            w = self.data['mxcell']['mxgeometry']['width']
        if h is None:
            h = self.data['mxcell']['mxgeometry']['height']

        self.data['coords']['x'] = x
        self.data['coords']['y'] = y
        self.data['coords']['width'] = w
        self.data['coords']['height'] = h

        self.data['mxcell']['mxgeometry']['x'] = self.data['coords']['x']
        self.data['mxcell']['mxgeometry']['y'] = self.data['coords']['y']
        self.data['mxcell']['mxgeometry']['width'] = self.data['coords']['width']
        self.data['mxcell']['mxgeometry']['height'] = self.data['coords']['height']
        mxCell = self.element.xpath('mxCell')
        mxGeo = mxCell[0].xpath('mxGeometry')
        for k,v in self.data['mxcell']['mxgeometry'].items():
            mxGeo[0].attrib[k] = str(v)

    def coords(self):
        x = int(self.data['mxcell']['mxgeometry']['x'])
        y = int(self.data['mxcell']['mxgeometry']['y'])
        width = int(self.data['mxcell']['mxgeometry']['width'])
        height = int(self.data['mxcell']['mxgeometry']['height'])

        self.data['coords']['x'] = x
        self.data['coords']['y'] = y
        self.data['coords']['w'] = width
        self.data['coords']['h'] = height
        self.data['coords']['tlc'] = {"x":x,"y":y}
        self.data['coords']['trc'] = {"x":x + width,"y":y}
        self.data['coords']['brc'] = {"x":x + width,"y":y + height}
        self.data['coords']['blc'] = {"x":x,"y":y + height}

        return self.data['coords']

    def has_tag(self,value):
        if 'tags' in self.data['attributes']:
            if value in self.data['attributes']['tags']:
                return True
        return False

    def set_tag(self,tag):
        if 'tags' in self.data['attributes']:
            if isinstance(self.data['attributes']['tags'],(str)):
                self.data['attributes']['tags'] = self.data['attributes']['tags'].split(",")

        if 'tags' not in self.data['attributes']:
            self.data['attributes']['tags'] = []

        self.data['attributes']['tags'].append(tag)
        self.element.attrib['tags'] = ','.join(self.data['attributes']['tags'])

    def remove_tag(self,tag):
        new_tags = []
        if 'tags' in self.data['attributes']:
            for t in self.data['attributes']['tags']:
                if t != tag:
                    new_tags.append(t)
        self.data['attributes']['tags']
        return False
