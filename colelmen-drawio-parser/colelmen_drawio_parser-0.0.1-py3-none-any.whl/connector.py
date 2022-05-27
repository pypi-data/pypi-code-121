
# import colemen_file_utils as cfu
import colemen_string_utils as csu
from lxml import etree
# import json
# import objectUtils as obj
from nodeBase import NodeBase
import utils.diagramUtils as dia

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
def new_connector(tree,diagram,source,target):
    o = etree.SubElement(diagram.dia_root, 'mxCell')
    # id = csu.gen.rand() if id is None else id
    o.attrib['id'] = csu.gen.rand()
    o.attrib['style']="edgeStyle=entityRelationEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    o.attrib['edge']="1"
    o.attrib['parent']="1"
    o.attrib['source']=source
    o.attrib['target']=target
    
    mxgeo = etree.SubElement(o, 'mxGeometry')
    mxgeo.attrib['relative'] = "1"
    mxgeo.attrib['as'] = "geometry"
    
    return Connector(tree,o,diagram)

class Connector(NodeBase):
    def __init__(self,tree,element=None,diagram=None):
        super().__init__(tree,element,diagram)
        self.settings = {}
        self.data = {}
        self._from_element()

    def _from_element(self):
        element = self.element
        if element is not None:
            self.data['attributes'] = dia.attrib_to_dict(element.attrib)
            return self.data

# edgeStyle=entityRelationEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;
    