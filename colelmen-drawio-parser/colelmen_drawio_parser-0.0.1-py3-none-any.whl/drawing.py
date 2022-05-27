
import colemen_file_utils as cfu
# import colemen_string_utils as csu
from lxml import etree
import json
import objectUtils as obj
import utils.diagramUtils as dia
from nodeBase import NodeBase
from connector import Connector
from onode import Onode
from diagram import new_diagram,Diagram


# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

def new_drawing():
    mxfile = etree.Element("mxfile")
    mxfile.attrib['host'] = "Electron"
    mxfile.attrib['modified'] = "2022-05-26T18:37:31.077Z" 
    mxfile.attrib['agent'] = "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) draw.io/14.9.6 Chrome/89.0.4389.128 Electron/12.0.16 Safari/537.36" 
    mxfile.attrib['etag'] = "AdGKFnLcEHsRAx8fGjjM" 
    mxfile.attrib['compressed'] = "false"
    mxfile.attrib['version'] = "14.9.6" 
    mxfile.attrib['type'] = "device"
    return Drawing(mxfile)

class Drawing(NodeBase):
    def __init__(self,tree,element=None):
        super().__init__(tree,element)
        self.settings = {}
        self.tree = tree
        self.element = element
        self.dia_root = None
        self.data = {
            "diagrams":[],
        }

        # self.set_defaults()
    def new_diagram(self,name):
        dia = new_diagram(self.tree,name)
        self.data['diagrams'].append(dia)
        return dia

    def save(self,path):
        # self.to_element()
        cfu.file.write.write(path,etree.tostring(self.tree).decode("utf-8"))
