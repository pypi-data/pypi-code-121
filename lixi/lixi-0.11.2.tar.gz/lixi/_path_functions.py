from lxml import etree
import re, time

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


def get_paths_for_elements(message=None, paths_list=None, schema=None):
    """
    Obtains all the element paths from a LIXI message or a paths list. In case of a paths list, obtains all the correct paths and referenced type paths.

    Args:
        message (:obj:`lixi._Message`, optional): A LIXI message instance.
        paths_list (:obj:`list`, optional): A Python list of paths.
        schema (:obj:`lxml.etree`, required): A etree object of a LIXI XML Annotated Schema.

    Returns:
        A Python list of paths that need to be included for customization. 
    """

    start = time.time()
    paths = []

    # Determine source
    if message != None:
        message_xml = message.xml_package
        message_tree = etree.ElementTree(message_xml)

        for e in message_tree.iter():
            # Get the base path of element, get it to lixi path
            element_path = message_tree.getpath(e)  ##Gets the path in lxml format
            element_path = element_path[1:]  ##Removes the first '/' from path
            element_path = element_path.replace(
                "/", "."
            )  ##Replaces '/' with '.' for LIXI Paths
            element_path = "".join(
                [i for i in element_path if not i.isdigit() and i != "[" and i != "]"]
            )  ##Removes numbers, and [] characters

            # Add base path
            if re.match(r"^[a-zA-Z0-9_@\.]*$", element_path):
                paths.append(element_path)

            # Check for elements attributes
            for att in e.attrib:
                att_path = element_path + "." + att

                if re.match(r"^[a-zA-Z0-9_@\.]*$", att_path):
                    paths.append(att_path)

    elif paths_list != None:
        # ensure element path is entered in the correct format
        for path in paths_list:
            schema_path_parent_breaks = path.split(".")
            append_path = ""

            for path_break in schema_path_parent_breaks:
                append_path = (
                    append_path + "." + path_break if append_path != "" else path_break
                )

                if append_path not in paths:
                    paths.append(append_path)

    paths.sort()
    # print(paths)
    final_paths = []
    complextype_paths = []
    simpletype_paths = []
    current_complex_type = None
    parent_path = None

    # dict of paths for effeciency, so lx:path xpath can be avoided
    dict_path_elem = {}
    all_schema_path_elements = schema.xpath("//lx:path", namespaces=ns)
    for path_elem in all_schema_path_elements:
        dict_path_elem[path_elem.text] = path_elem

    # unravel all complexTypes
    for message_path in paths:

        if re.match(r"^[a-zA-Z0-9_@\.]*$", message_path):

            if message_path not in dict_path_elem:

                # A case when exploded complex paths come which are non searchable, so they have to be broken into something that can be searched in an unexploded schema
                orig_message_path = message_path
                #print(orig_message_path)
                cut_message_path = message_path.replace(parent_path, "")
                message_path = current_complex_type + cut_message_path

                ##complex within a complex
                if message_path not in dict_path_elem:

                    paths = cut_message_path[1:].split(".")
                    index = 0
                    is_complex = False
                    new_complex_type = current_complex_type
                    found_complex = None

                    while is_complex == False:
                        new_complex_type = new_complex_type + "." + paths[index]

                        find_it = schema.xpath(
                            '//xs:element/xs:annotation/xs:appinfo/lx:path[text()="'
                            + new_complex_type
                            + '"]',
                            namespaces=ns,
                        )
                        if len(find_it) > 0:
                            if (
                                "type"
                                in find_it[0].getparent().getparent().getparent().attrib
                            ):
                                is_complex = True
                                found_complex = (
                                    find_it[0]
                                    .getparent()
                                    .getparent()
                                    .getparent()
                                    .attrib["type"]
                                )
                            else:
                                index = index + 1
                        else:
                            index = index + 1

                    if found_complex != None:

                        remaining_path = message_path.replace(new_complex_type, "")

                        if found_complex not in complextype_paths:
                            complextype_paths.append(found_complex)

                        message_path = found_complex + remaining_path

                searched_simple_path = dict_path_elem[message_path]
                searched_simple_parent = (
                    searched_simple_path.getparent().getparent().getparent()
                )

                if "type" in searched_simple_parent.attrib:
                    typename = searched_simple_parent.attrib["type"]

                    if typename in dict_path_elem:
                        if typename not in simpletype_paths:
                            simpletype_paths.append(typename)

                if message_path not in complextype_paths:
                    complextype_paths.append(message_path)

            else:

                # case when path is searchable
                parent = (
                    dict_path_elem[message_path].getparent().getparent().getparent()
                )

                if "type" in parent.attrib:
                    typename = parent.attrib["type"]

                    if typename in dict_path_elem:
                        searched_path = (
                            dict_path_elem[typename].getparent().getparent().getparent()
                        )
                        tag = searched_path.tag

                        if tag == "{http://www.w3.org/2001/XMLSchema}complexType":
                            current_complex_type = typename
                            parent_path = message_path

                            if typename not in complextype_paths:
                                complextype_paths.append(typename)

                        elif tag == "{http://www.w3.org/2001/XMLSchema}simpleType":

                            if typename not in simpletype_paths:
                                simpletype_paths.append(typename)

                final_paths.append(message_path)

    # simpleTypes
    for simple_type in simpletype_paths:
        last_four = simple_type[-4:]

        if last_four == "List":
            searched_simple_path = schema.xpath(
                './xs:simpleType[@name="' + simple_type + '"]', namespaces=ns
            )
            simpletype_paths = simpletype_paths + searched_simple_path[0].xpath(
                "./xs:restriction/xs:enumeration/xs:annotation/xs:appinfo/lx:path/text()",
                namespaces=ns,
            )

    final_paths.sort()
    complextype_paths.sort()
    simpletype_paths.sort()

    final_paths = final_paths + complextype_paths + simpletype_paths
    final_paths = list(dict.fromkeys(final_paths))
    return final_paths

def get_exploded_paths_for_schema_elements(annotated_schema):
    """
    Gets all the ecploded element paths from a LIXI XML schema.

    Args:
        annotated_schema (:obj:`lxml.etree`, required): A etree object of a LIXI XML Annotated Schema.
            
    Returns:
        A Python list of paths in the LIXI Schema. 
    """
    
    exploded_schema = _explode_schema.main(annotated_schema)
    
    return exploded_schema.xpath("//lx:path/text()", namespaces=ns)
    
    ## dict of paths for effeciency, so lx:path xpath can be avoided
    #package = annotated_schema.xpath("./xs:element", namespaces=ns)
    #complex_types = annotated_schema.xpath("./xs:complexType//lx:path/text()", namespaces=ns)
    #simple_types = annotated_schema.xpath("./xs:simpleType//lx:path/text()", namespaces=ns)
    
    #element_paths = package[0].xpath("//xs:element/xs:annotation/xs:appinfo/lx:path", namespaces=ns)
    #attribute_paths = package[0].xpath("//xs:attribute/xs:annotation/xs:appinfo/lx:path/text()", namespaces=ns)
    
    #all_element_paths = []
    #for lxpath in element_paths:
        
        #if 'type' in lxpath.getparent().getparent().getparent().attrib:
            
            #complextype = lxpath.getparent().getparent().getparent().attrib['type']
            #if complextype in complex_types:
                
                #parent_path = lxpath.text
                #for complex_path in complex_types:
                    #if complextype in complex_path:
                        #all_element_paths.append(complex_path.replace(complextype, parent_path))
                
            #else:
                #all_element_paths.append(lxpath.text)
        #else:
            #all_element_paths.append(lxpath.text)
                
    
    #final_paths = all_element_paths + attribute_paths + simple_types
    #final_paths.sort()
    
    ##print(json.dumps(final_paths, indent=3))
    
    #return final_paths

def get_paths_for_schema_elements(annotated_schema):
    """
    Gets all the element paths from a LIXI XML schema.

    Args:
        annotated_schema (:obj:`lxml.etree`, required): A etree object of a LIXI XML Annotated Schema.
            
    Returns:
        A Python list of paths in the LIXI Schema. 
    """
    # Xpath to get all schema element paths
    return annotated_schema.xpath("//lx:path/text()", namespaces=ns)


def get_blacklist_paths_for_customization(
    transaction_type, message_paths, schema_paths
):
    """
    Generates a string of blacklist customization restrictions xml for a customized LIXI schema.

    Args:
        transaction_type (:obj:`str`, required): The transaction type of the LIXI schema.
        message_paths (:obj:`lxml.etree`, required): All element paths from a LIXI message.
        schema_paths (:obj:`lxml.etree`, required): All element paths from a LIXI schema.
            
    Returns:
        A string of blacklist customization restrictions xml that can be utilized by this library to generate a custom schema.  
    """

    # Get list of paths to remove:
    paths_to_remove = set(schema_paths) - set(message_paths)
    paths_to_remove = list(paths_to_remove)

    paths_to_remove.sort()

    # Form a string of customization instructions.
    customization_instructions = ""
    customization_instructions += (
        '''<Customisations xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="LIXI-Customisation-By-Restriction.xsd" LIXICode="LIXILIXI" CustomisationCode="v1" LIXITransactionType="'''
        + transaction_type
        + """">\n"""
    )

    # Some paths that can't be removed as they are reserved.
    paths_that_cant_removed = [
        "Package",
        "Package.SchemaVersion",
        "Package.SchemaVersion.LIXICustomVersion",
        "Package.SchemaVersion.LIXITransactionType",
        "Package.SchemaVersion.LIXIVersion",
        "Package.Publisher",
        "Package.Publisher.LIXICode",
        "Package.Recipient",
        "Package.Recipient.LIXICode",
        "Package.Instructions",
        "Package.Instructions.AccountCreationInstructions",
        "Package.Instructions.AccountCreationInstructions.Submit",
        "Package.Instructions.ApplicationInstructions",
        "Package.Instructions.ApplicationInstructions.Submit",
        "Package.Instructions.CreditDecisionInstructions",
        "Package.Instructions.CreditDecisionInstructions.Submit",
        "Package.Instructions.DocumentsAndSettlementInstructions",
        "Package.Instructions.DocumentsAndSettlementInstructions.Submit",
        "Package.Instructions.LendersMortgageInsuranceInstructions",
        "Package.Instructions.LendersMortgageInsuranceInstructions.Submit",
        "Package.Instructions.ServiceabilityInstructions",
        "Package.Instructions.ServiceabilityInstructions.Submit",
        "Package.Instructions.ValuationInstructions",
        "Package.Instructions.ValuationInstructions.Submit",
    ]
    
    
    #If parent removed then no need to add child.
    redo_list = []
    for path in paths_to_remove:
        if path not in paths_that_cant_removed:
            
            if '.' in path:
                
                parent_in = False
                
                splits = path.split('.')
                
                i=0
                check_path = splits[i]
                while check_path != path:
                    
                    if check_path in redo_list:
                        parent_in = True
                    
                    i = i + 1
                    check_path = check_path + '.'+ splits[i]
                
                if parent_in == False:
                    redo_list.append(path)
            else:
                redo_list.append(path)
    
    #If simpletype/complextype are removed from base then no need to add that in instructions as it clutters it and custom schema already handles it anyhow.
    redo_redo_list = []
    for path in redo_list:
        if 'Package' in path or '.' in path:
            redo_redo_list.append(path)
    
    
    for path in redo_redo_list:

        if path not in paths_that_cant_removed:
            customization_instructions += (
                '<CustomiseItem Exclude="Yes"><Path>'
                + path
                + "</Path></CustomiseItem>\n"
            )

    customization_instructions += "</Customisations>"
    #with open('./simp/ins.xml','w+') as f:
        #f.write(customization_instructions)
        
    return customization_instructions
