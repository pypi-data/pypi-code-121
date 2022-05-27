
# import colemen_file_utils as cfu
import colemen_string_utils as csu
from lxml import etree
import json
import objectUtils as obj
import utils.diagramUtils as dia
from connector import Connector
from mcxell import Mxcell,new_mxcell
from onode import Onode,new_onode
from connector import Connector,new_connector


# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

def new_diagram(drawing,name=None):
    if name is None:
        name = csu.gen.rand()
    diagram = etree.SubElement(drawing, 'diagram')
    # diagram = etree.Element("diagram")
    diagram.attrib['id'] = csu.gen.rand(20)
    diagram.attrib['name'] = name

    mxgm_data = {
        "dx":"1074",
        "dy":"954",
        "grid":"1",
        "gridSize":"10",
        "guides":"1",
        "tooltips":"1",
        "connect":"1",
        "arrows":"1",
        "fold":"1",
        "page":"1",
        "pageScale":"1",
        "pageWidth":"1700",
        "pageHeight":"1100",
        "math":"0",
        "shadow":"0",
    }

    mxGraphModel = etree.SubElement(diagram, 'mxGraphModel')
    for k,v in mxgm_data.items():
        mxGraphModel.attrib[k] = v
        
    root = etree.SubElement(mxGraphModel, 'root')
    d = Diagram(drawing,diagram)
    d.add_mxcell("0")
    d.add_mxcell("1","0")
    return d



class Diagram:
    def __init__(self,tree,element=None):
        self.settings = {}
        self.tree = tree
        self.element = element
        self.dia_root = None
        self.data = {
            "attributes":{},
            "connectors":[],
            "children":[],
        }

        self._from_element()
        # self.set_defaults()

    def _from_element(self):
        element = self.element
        if element is not None:
            self.dia_root = dia.get_diagram_root_node(element)[0]
            self.data['attributes'] = dia.attrib_to_dict(element.attrib)
            # self.data['connectors'] = dia.get_connectors(element)
            children = dia.get_children(self.dia_root)
            # print(f"children: {children}")

            for c in children:
                if c.tag =="mxCell":
                    if 'source' in c.attrib:
                        con = Connector(self.tree,c,self)
                        self.data['connectors'].append(con)
                        # self.data['connectors']
                        # print(f"connector Found: {c}")
                    else:
                        print(f"mxcell found: {c}")

                if c.tag == "object":
                    O = Onode(self.tree,c,self)
                    self.data['children'].append(O)
                    # print(f"object found: {c}")
                # self.data['children']['id'] = c.attrib['id']

            return self.data

    def list_node_labels(self):
        for x in self.data['children']:
            label = x.get_label(None)
            if label is not None:
                print(label)

    def add_mxcell(self,id=None,parent=None):
        cell = new_mxcell(self.tree,self,id,parent)
        self.data['children'].append(cell)

    def add_onode(self,id=None):
        cell = new_onode(self.tree,self,id)
        self.data['children'].append(cell)
        return cell

    def add_connector(self,source,target):
        cell = new_connector(self.tree,self,source,target)
        self.data['connectors'].append(cell)
        return cell

    def get_nodes_by_tag(self,tag):
        nodes = []
        for c in self.data['children']:
            if c.has_tag(tag):
                nodes.append(c)
        return nodes
    # def next_avail_y(self,x,y):


    # def is_intersecting(self,coords):
    #     for c in self.data['children']:
    #         if coords['trc']['x'] < c.coords()['trc']['x']:
                