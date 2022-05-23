import os, glob, re, isodate, datetime, pkg_resources, io, json
from decimal import *
from lxml import etree as elemTree
from xmljson import BadgerFish
from collections import OrderedDict
from operator import attrgetter

if __name__ == "_LIXI":
    import _explode_schema
else:
    from lixi import (
        _explode_schema
    )

ns = {
    "xs": "http://www.w3.org/2001/XMLSchema",
    "lx": "lixi.org.au/schema/appinfo_elements",
    "li": "lixi.org.au/schema/appinfo_instructions",
}

def build_types(annotated_schema_obj):
    simpletype_mappings = {}
    type_mappings = {
        "anyType":  "string",
        "anySimpleType":  "string",
        "string":  "string",
        "normalizedString":  "string",
        "token":  "string",
        "language":  "string",
        "Name":  "string",
        "NCName":  "string",
        "ID":  "id",
        "IDREF":  "idref",
        "IDREFS":  "idref",
        "ENTITY":  "string",
        "ENTITIES":  "string",
        "NMTOKEN":  "string",
        "NMTOKENS": "string",
        "boolean": "boolean",
        "base64Binary": "base64",
        "hexBinary": "string",
        "float": "number",
        "decimal": "number",
        "integer": "integer",
        "nonPositiveInteger": "integer",
        "negativeInteger": "integer",
        "long": "integer",
        "int": "integer",
        "short": "integer",
        "byte": "integer",
        "nonNegativeInteger": "integer",
        "unsignedLong": "integer",
        "unsignedInt": "integer",
        "unsignedShort": "integer",
        "unsignedByte": "integer",
        "positiveInteger": "integer",
        "double": "number",
        "anyURI": "string",
        "QName": "string",
        "NOTATION": "string",
        "duration": "string",
        "dateTime": "datetime",
        "date": "date",
        "time": "string",
        "gYearMonth": "string",
        "gYear": "year",
        "gMonthDay": "string",
        "gDay": "string",
        "gMonth": "string"
    }
    
    exploded_annotated_schema_obj = _explode_schema.main(annotated_schema_obj)
    
    elementsandatt_mappings = {}

    for element in exploded_annotated_schema_obj.iter():
        if "www.w3.org" in element.tag:
            if "simpleType" in element.tag:
                element_name = element.attrib.get("name")
                element_type = element.find("xs:restriction", ns).attrib["base"]
                if "xs:" in element_type:
                    element_type = element_type[3:]

                simpletype_mappings[element_name] = element_type

            elif "attribute" in element.tag:
                element_path = element.find('./xs:annotation/xs:appinfo/lx:path', ns).text
                element_type = element.attrib["type"]

                elementsandatt_mappings[element_path] = element_type    

            elif "element" in element.tag:
                element_path = element.find('./xs:annotation/xs:appinfo/lx:path', ns).text
                
                if 'maxOccurs' in element.attrib:
                    if element.attrib["maxOccurs"] == '1':
                        element_max = 'obj'
                    else:
                            element_max = 'arr'
                else:
                    element_max = 'obj'  

                elementsandatt_mappings[element_path] = element_max

    for k,v in elementsandatt_mappings.items():
        if v in simpletype_mappings:
            elementsandatt_mappings[k] = type_mappings[simpletype_mappings[v]]

    return elementsandatt_mappings        

def to_json(xml_etree, xsd_annotated_schema):
    """ Converts a Python XML etree to JSON etree and arranges the result per schema.
    
    Args:
        xml_etree (:obj:`lxml.etree`, required): XML Message to convert to JSON message.
        xsd_annotated_schema (:obj:`lxml.etree`, required): A LIXI XML Schema.
    
    Returns:
        A python JSON dict object.
    
    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
    """

    json_object = {}

    def json_change_types(json_obj, parent_path, mappings):
        
        for key ,value in json_obj.items():

            this_elem_path = None
            if parent_path=='':
                this_elem_path = key
            else:
                this_elem_path = parent_path +'.'+ key
        
            if isinstance(value, list):
                for array_item in value:
                    json_change_types(array_item, this_elem_path, mappings)
                    
            elif isinstance(value, dict):
                if this_elem_path in mappings:
                    if mappings[this_elem_path]=='arr':
                        json_obj[key] = [value]
                        
                        for array_item2 in json_obj[key]:
                            json_change_types(array_item2, this_elem_path, mappings) 
                    else:
                        json_change_types(value, this_elem_path, mappings)
                else:
                    json_change_types(value, this_elem_path, mappings)
            else:
                this_elem_path = this_elem_path.replace('@','')
                if this_elem_path in mappings:
                    lookup = mappings[this_elem_path]
    
                    if "number" == lookup or "decimal" == lookup or "float" == lookup:
                        json_obj[key] = float(value)
                    elif "integer" == lookup:
                        json_obj[key] = int(value)

        return json_obj

    bf = BadgerFish(xml_fromstring=False)
    json_object = bf.data(xml_etree)

    mappings = build_types(xsd_annotated_schema)

    json_object = json_change_types(json_object, '', mappings)
      
    return json_object


def to_json_string(xml_str, xsd_annotated_schema_str):
    """ Converts a Python XML string to JSON string and arranges the result per schema.
    
    Args:
        xml_str (:obj:`str`, required): XML Message string to convert to JSON message.
        xsd_annotated_schema_str (:obj:`str`, required): A LIXI XML Schema string.
    
    Returns:
        A python JSON string message object.
    
    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
    """

    xml_etree = elemTree.fromstring(xml_str)
    xsd_annotated_schema = elemTree.fromstring(xsd_annotated_schema_str)

    converted_json = to_json(xml_etree, xsd_annotated_schema)
    return json.dumps(converted_json, sort_keys=True, indent=4, ensure_ascii=False)


def to_xml(json_dict, xsd_annotated_schema):
    """ Converts a Python JSON dict to XML etree and arranges the result per schema.
    
    Args:
        json_dict (:obj:`dict`, required): JSON Message string to convert to XML message.
        xsd_annotated_schema (:obj:`lxml.etree`, required): A LIXI XML Schema string.
    
    Returns:
        A python XML Etree object.
    
    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
    """

    def xml_get_sorted_list(schema_root):
        sorting_elem_list = {}
        sorting_list = {}
        sorting_complex_list = {}

        for elem in schema_root.iter(tag=("{*}element", "{*}complexType")):

            if "element" in elem.tag and elem.attrib.get("name") is not None:
                if elem.attrib.get("type") is None:
                    key_name = (
                        str(
                            elem.xpath(
                                "./xs:annotation/xs:appinfo/lx:path/text()",
                                namespaces=ns,
                            )
                        )
                        .strip("[]'")
                        .replace(".", "/")
                    )

                    if (
                        elem.find(
                            "./xs:complexType/xs:sequence/xs:element", namespaces=ns
                        )
                        is not None
                    ):
                        sorting_elem_list[key_name] = []
                        for child_xsd_element in elem.xpath(
                            "./xs:complexType/xs:sequence/xs:element", namespaces=ns
                        ):
                            sorting_elem_list[key_name].append(
                                child_xsd_element.attrib.get("name")
                            )

                    elif (
                        elem.find(
                            "./xs:complexType/xs:choice/xs:element", namespaces=ns
                        )
                        is not None
                    ):
                        sorting_elem_list[key_name] = []
                        for child_xsd_element in elem.findall(
                            "./xs:complexType/xs:choice/xs:element", namespaces=ns
                        ):
                            sorting_elem_list[key_name].append(
                                child_xsd_element.attrib.get("name")
                            )

                elif elem.attrib.get("type") is not None:
                    key_name = (
                        str(
                            elem.xpath(
                                "./xs:annotation/xs:appinfo/lx:path/text()",
                                namespaces=ns,
                            )
                        )
                        .strip("[]'")
                        .replace(".", "/")
                    )
                    sorting_elem_list[key_name + "/" + elem.attrib.get("type")] = []

            elif "complexType" in elem.tag:
                if elem.attrib.get("name") is not None:
                    key_name = (
                        str(
                            elem.xpath(
                                "./xs:annotation/xs:appinfo/lx:path/text()",
                                namespaces=ns,
                            )
                        )
                        .strip("[]'")
                        .replace(".", "/")
                    )

                    if elem.find("./xs:sequence/xs:element", namespaces=ns) is not None:
                        sorting_complex_list[key_name] = []
                        for child_xsd_element in elem.xpath(
                            "./xs:sequence/xs:element", namespaces=ns
                        ):
                            sorting_complex_list[key_name].append(
                                child_xsd_element.attrib.get("name")
                            )

        for k, v in sorting_complex_list.items():
            for key, value in sorting_elem_list.items():
                if k in key:
                    sorting_list["/" + key.replace("/" + k, "")] = v

        for k, v in sorting_elem_list.items():
            if len(v) > 0:
                sorting_list["/" + k] = v

        return sorting_list

    def xml_sort_message(unsorted_xml, sorting_list):

        tree = elemTree.ElementTree(unsorted_xml)

        for e in unsorted_xml.xpath("//*"):

            keys = e.attrib
            sorted_attrib = OrderedDict(sorted(keys.items()))
            e.attrib.clear()
            e.attrib.update(sorted_attrib)

            elem_path_key = tree.getpath(e).strip("[0123456789]")

            if elem_path_key in sorting_list:
                e[:] = sorted(
                    e, key=lambda elem: get_elem_key(elem, elem_path_key, sorting_list)
                )

        return unsorted_xml

    def get_elem_key(elem, elem_path_key, sorting_list):

        try:
            if sorting_list[elem_path_key].index(elem.tag) is not None:
                return sorting_list[elem_path_key].index(elem.tag)
            else:
                return 0
        except:
            return 0

    bf = BadgerFish()
    unsorted_xml = bf.etree(json_dict)[0]

    sorting_list = xml_get_sorted_list(xsd_annotated_schema)
    converted_sorted_xml = xml_sort_message(unsorted_xml, sorting_list)

    return converted_sorted_xml


def to_xml_string(json_str, xsd_annotated_schema_str):
    """ Converts a Python JSON string to XML string and arranges the result per schema.
    
    Args:
        json_str (:obj:`str`, required): JSON Message string to convert to XML message.
        xsd_annotated_schema_str (:obj:`str`, required): A LIXI XML Schema string.
    
    Returns:
        A python XML string message object.
    
    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
    """

    json_dict = json.loads(json_str)
    xsd_annotated_schema = elemTree.fromstring(xsd_annotated_schema_str)

    converted_xml = to_xml(json_dict, xsd_annotated_schema)
    return elemTree.tostring(converted_xml, pretty_print=True).decode("utf-8")
