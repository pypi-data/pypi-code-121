from xml.etree import ElementTree
from xml_flatten import *

tree = ElementTree.parse("./nested_xml_sample.xml")
root = tree.getroot()

for i in root:
    res=rec(i,1,"root")
    for i in  xml_flat:
        print(i)