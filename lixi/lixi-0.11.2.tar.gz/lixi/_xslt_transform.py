import os, re, filecmp, sys, datetime, html, inspect, lxml, pkg_resources, glob, zipfile, io, xml.dom.minidom as dome
from operator import attrgetter
from shutil import copyfile
from lxml import etree
from lxml import builder

ns = {
    "xs": "http://www.w3.org/2001/XMLSchema",
    "lx": "lixi.org.au/schema/appinfo_elements",
    "li": "lixi.org.au/schema/appinfo_instructions",
}


def apply_xslt(xmlFile, xsltFile):
    """ Applys a xslt rule file to a XML message.
    
    Args:
        xmlFile (:obj:`lxml.etree`, required): A XML Message.
        xsltFile (:obj:`lxml.etree`, required): A XSLT transform rules file.
    
    Returns:
        A string of result XML.
    
    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
    """

    xslt = etree.parse(xsltFile)
    transform = etree.XSLT(xslt)
    newdom = transform(xmlFile)
    outstr = etree.tostring(
        newdom, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )

    return outstr


def transform_xslt(sample_etree, xslt_folder_path, transaction_type, from_version_str, to_version_str):
    """ Transforms a LIXI Message instance to an older/newer version, based on the schema version specified, of the LIXI Message instance.
    
    Args:
        sample_etree (:obj:`str`, required): A LIXI Message provided as a string. Defaults to None.
        xslt_folder_path (:obj:`bool`, required): A path to a folder containing LIXI transformation (.xslt) files. 
        transaction_type (:obj:`bool`, required): The transaction type of a LIXI schema. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None.
        from_version_str (:obj:`str`, required): The version of the LIXI schema to be transformed to. Should be in the format of '2.6.24'. 
        to_version_str (:obj:`str`, required): The version of the LIXI schema to be transformed to. Should be in the format of '2.6.24'. 

    Returns:
        Transformed LIXI Message instance ONLY if return_instance is set to True.

    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
    """

    def sort_versions(tranforms):
        temp_list = []

        def num_keyfn(x):
            parts = x.split("_")
            return tuple(int(x) if x.isnumeric else x for x in parts)

        for num in sorted(tranforms, key=num_keyfn):
            temp_list.append(num)

        return temp_list

    # Determine if its a backwards or forwards transformation (assumption, version provided by user is of the form '#.#.#')
    to_version = to_version_str.split(".")
    from_version = from_version_str.split(".")

    if int(to_version[0]) == int(from_version[0]):
        if int(to_version[1]) == int(from_version[1]):
            if int(to_version[2]) == int(from_version[2]):
                return sample_etree, ""
            elif int(to_version[2]) > int(from_version[2]):
                direction = "forwards"
            elif int(to_version[2]) < int(from_version[2]):
                direction = "backwards"
        elif int(to_version[1]) > int(from_version[1]):
            direction = "forwards"
        elif int(to_version[1]) < int(from_version[1]):
            direction = "backwards"
    elif int(to_version[0]) > int(from_version[0]):
        direction = "forwards"
    elif int(to_version[0]) < int(from_version[0]):
        direction = "backwards"

    # Vars help order the final list correctly
    if direction == "forwards":
        greater_version_no = (
            "LIXI-" + transaction_type + "-" + to_version_str.replace(".", "_")
        )
        lesser_version_no = (
            "LIXI-" + transaction_type + "-" + from_version_str.replace(".", "_")
        )
    else:
        greater_version_no = (
            "LIXI-" + transaction_type + "-" + from_version_str.replace(".", "_")
        )
        lesser_version_no = (
            "LIXI-" + transaction_type + "-" + to_version_str.replace(".", "_")
        )

    # The complete version lists
    tranforms = []
    #for filename in glob.glob(
        #os.path.join(pkg_resources.resource_filename(__name__, "xslts"), "*.xsl")
    #):
    for filename in glob.glob(
        os.path.join(xslt_folder_path, "*.xsl")
    ):        
        if "warnings" not in filename and transaction_type in filename:
            filename = re.search(
                r"LIXI-([a-zA-Z0-9_-]*).xsl", filename.replace("LIXI", "", 1)
            ).group(1)
            filename = filename.replace(transaction_type + "-", "")
            if filename not in tranforms:
                tranforms.append(filename)
    tranforms = sort_versions(tranforms)
    tranforms_versions = [
        ("LIXI-" + transaction_type + "-" + x.replace(".", "_")) for x in tranforms
    ]

    # Create a list of only required version/transaction strings and in the correct order.
    count_forwards = []
    count_backwards = []
    tranforms_list = []
    check = False

    for version in tranforms_versions:
        if version == lesser_version_no or check == True:
            count_forwards.append(version)
            check = True

    check = False
    count_forwards = list(reversed(count_forwards))
    for version in count_forwards:
        if version == greater_version_no or check == True:
            count_backwards.append(version)
            check = True

    if direction == "forwards":
        tranforms_list = list(reversed(count_backwards))
    else:
        tranforms_list = count_backwards

    tranforms_forwards, tranforms_backwards = (
        count_backwards,
        list(reversed(count_backwards)),
    )

    if direction == "forwards":
        tranforms_forwards, tranforms_backwards = (
            tranforms_backwards,
            tranforms_forwards,
        )

    # The actual transformation of the files from one version to all prev versions
    step = 0

    temp_prev_step_xml = sample_etree
    temp_current_step_xml = None
    temp_step_warnings_xml = etree.Element(
        "{http://www.w3.org/2001/XMLSchema-instance}warnings"
    )

    for first, second in zip(tranforms_list, tranforms_list[1:]):

        #archive = zipfile.ZipFile(
            #os.path.join(
                #pkg_resources.resource_filename(__name__, "xslts"),
                #first + "-" + second + ".zip",
            #),
            #"r",
        #)
        #stylesheet = io.BytesIO(archive.read(first + "-" + second + ".xsl"))
        stylesheet = os.path.join(xslt_folder_path,first + "-" + second + ".xsl")
        
        #archive = zipfile.ZipFile(
            #os.path.join(
                #pkg_resources.resource_filename(__name__, "xslts"),
                #first + "-" + second + "-warnings.zip",
            #),
            #"r",
        #)
        #warningsheet = io.BytesIO(archive.read(first + "-" + second + "-warnings.xsl"))
        warningsheet = os.path.join(xslt_folder_path, first + "-" + second + "-warnings.xsl")
        
        # schemafile   = os.path.join(xsd_folder_path, second + "-Annotated.xsd")

        # print(stylesheet + "\t\t" + "-step-" + str(step + 1), end="")

        # do the XSL transformation
        temp_current_step_xml = etree.fromstring(
            apply_xslt(temp_prev_step_xml, stylesheet)
        )

        # step
        comment = etree.Comment(" Step " + str(step) + " ")
        temp_step_warnings_xml.append(comment)

        # create warnings for this transformation
        temp_current_step_warnings_xml = etree.fromstring(
            apply_xslt(temp_prev_step_xml, warningsheet)
        )
        for child in temp_current_step_warnings_xml:
            temp_step_warnings_xml.append(child)

        # Validate the resulting XML against the correct schema
        # schema_etree = etree.parse(schemafile)
        # schema = etree.XMLSchema(schema_etree)
        # valid = schema.validate(temp_current_step_xml)
        # valid = True
        # if valid:
        # print("\t...valid")

        # else:
        # print("\n")
        # for error in schema.error_log:
        # print("ERROR ON LINE "+str(error.line)+": "+str(error.message.encode("utf-8"))+".")
        # raise Exception("ERROR: tranformed message is not valid, "+str(step + 1)+".")

        temp_prev_step_xml = temp_current_step_xml
        step = step + 1

    xml_string = etree.tostring(temp_step_warnings_xml).decode()
    xml_string = xml_string.strip().replace(">\n", ">").replace("\n<", "<")
    reparsed = dome.parseString(xml_string)
    all_warnings = reparsed.toprettyxml(indent="  ")

    return temp_current_step_xml, all_warnings
