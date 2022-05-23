from lxml import etree
from datetime import datetime
import os, io, glob, copy, pkg_resources, xml.etree.ElementTree, xml.dom.minidom as dome
from os import name, path, makedirs
import errno, time


class LIXIValidationError(Exception):
    def __init__(self, message, message_instance=None):
        super().__init__(message)
        self.message_instance = message_instance


def CustomiseSingleSchema(
    schema_to_customise,
    customisation_instruction_file,
    schema_documentation_text,
    lixi_custom_version_code,
    namespaces,
):
    """
    Create a custom schema based on customization restrictions xml.

    Args:
        schema_to_customise (:obj:`lxml.etree`, required): LIXI schema that the subschema is bein derived from.
        customisation_instruction_file (:obj:`lxml.etree`, required): Customization instructions provided as a Python etree.
        schema_documentation_text (:obj:`str`, required): Annotation text of the custom schema to be added up top.
        lixi_custom_version_code (:obj:`str`, required): Name of the produced custom schema.
        namespaces (:obj:`lxml.etree`, required): Namespaces to be used in creating this custom schema.
            
    Returns:
        A Python etree of the produced XML Custom LIXI schema.
        
    Raises:
        LIXIValidationError: Validation errors in the file.
        
    """

    # Set up the Log File Variable
    warningList = []

    # Parse the schema and get the root element
    xmlParsedSchemaRoot = schema_to_customise

    # Update the second Schema documentation element
    xmlParsedSchemaRoot.xpath(
        "./xs:annotation/xs:documentation[2]", namespaces=namespaces
    )[0].text = schema_documentation_text

    xmlSchemaAppinfo = etree.XPathEvaluator(xmlParsedSchemaRoot, namespaces=namespaces)(
        "./xs:annotation/xs:appinfo"
    )[0]

    source_transaction_schema_type = xmlParsedSchemaRoot.xpath(
        "./xs:annotation/xs:appinfo/lx:schemadetail/@version", namespaces=namespaces
    )[0]

    source_transaction_schema_version = xmlParsedSchemaRoot.xpath(
        "./xs:annotation/xs:appinfo/lx:schemadetail/@transaction", namespaces=namespaces
    )[0]

    xmlSchemaCustomisation = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}schemacustomisation"
    )
    xmlSchemaCustomisation.tail = "\n"
    xmlSchemaAppinfo.insert(1, xmlSchemaCustomisation)

    xmlBlacklist = etree.Element("{lixi.org.au/schema/appinfo_instructions}Exclude")
    xmlBlacklist.tail = "\n"
    xmlSchemaCustomisation.append(xmlBlacklist)

    xmlOptionalToMandatory = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}OptionalToMandatory"
    )
    xmlOptionalToMandatory.tail = "\n"
    xmlSchemaCustomisation.append(xmlOptionalToMandatory)

    xmlStringToEnum = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}StringToList"
    )
    xmlStringToEnum.tail = "\n"
    xmlSchemaCustomisation.append(xmlStringToEnum)

    xmlStringToPattern = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}StringToPattern"
    )
    xmlStringToPattern.tail = "\n"
    xmlSchemaCustomisation.append(xmlStringToPattern)

    xmlCustomMaxOccurs = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomMaxOccurs"
    )
    xmlCustomMaxOccurs.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomMaxOccurs)

    xmlCustomMinOccurs = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomMinOccurs"
    )
    xmlCustomMinOccurs.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomMinOccurs)

    xmlCustomCurrencyRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomCurrencyRange"
    )
    xmlCustomCurrencyRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomCurrencyRange)

    xmlCustomDateTimeRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomDateTimeRange"
    )
    xmlCustomDateTimeRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomDateTimeRange)

    xmlCustomDateRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomDateRange"
    )
    xmlCustomDateRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomDateRange)

    xmlCustomDecimalRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomDecimalRange"
    )
    xmlCustomDecimalRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomDecimalRange)

    xmlCustomYearRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomYearRange"
    )
    xmlCustomYearRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomYearRange)

    xmlCustomIntegerRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomIntegerRange"
    )
    xmlCustomIntegerRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomIntegerRange)

    xmlCustomPercentageRange = etree.Element(
        "{lixi.org.au/schema/appinfo_instructions}CustomPercentageRange"
    )
    xmlCustomPercentageRange.tail = "\n"
    xmlSchemaCustomisation.append(xmlCustomPercentageRange)

    xmlSchemaDetail = etree.XPathEvaluator(xmlParsedSchemaRoot, namespaces=namespaces)(
        "/xs:schema/xs:annotation/xs:appinfo/lx:schemadetail"
    )[0]
    xmlSchemaDetail.attrib["type"] = "Custom"
    xmlSchemaDetail.attrib["version"] = lixi_custom_version_code
    xmlSchemaDetail.attrib["transactionschemasource"] = (
        source_transaction_schema_version + " " + source_transaction_schema_type
    )

    # On the LIXICustomVersion field, we need to change the optional flag to mandatory and insert the LIXICustomVersion value
    xmlLIXICustomVersion = xmlParsedSchemaRoot.xpath(
        '/xs:schema/xs:element/xs:complexType/xs:sequence/xs:element["SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXICustomVersion"]',
        namespaces=namespaces,
    )[0]
    xmlLIXICustomVersion.attrib["use"] = "required"
    xmlLIXICustomVersion.attrib["fixed"] = lixi_custom_version_code

    # Read the instruction file
    instruction_file_root = customisation_instruction_file
    sequence = 0

    all_instructions = instruction_file_root.xpath("//CustomiseItem")
    for ins in all_instructions:
        ins.set("linenumber", str(ins.sourceline))

    # Create a list of all paths for blacklist/exclude and whitelist/include operations
    dict_path_elem = {}
    all_schema_path_elements = xmlParsedSchemaRoot.xpath(
        "//lx:path", namespaces=namespaces
    )  #
    for path_elem in all_schema_path_elements:
        dict_path_elem[path_elem.text] = path_elem

    # get all whitelist paths in instructions
    restrictMethod = "Include"
    whitelist_paths = []
    whitelist_paths = whitelist_paths + instruction_file_root.findall(
        "CustomiseItem[@Include='Yes']"
    )
    whitelist_paths = whitelist_paths + instruction_file_root.findall(
        "CustomiseItem[@Whitelist='Yes']"
    )

    for row in whitelist_paths:
        pathToRestrict = row.find("Path").text
        linenum = str(row.get("linenumber"))

        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        elif (
            dict_path_elem[pathToRestrict].getparent().getparent().getparent().tag
            != "{http://www.w3.org/2001/XMLSchema}element"
            and dict_path_elem[pathToRestrict].getparent().getparent().getparent().tag
            != "{http://www.w3.org/2001/XMLSchema}simpleType"
            and dict_path_elem[pathToRestrict].getparent().getparent().getparent().tag
            != "{http://www.w3.org/2001/XMLSchema}complexType"
            and dict_path_elem[pathToRestrict].getparent().getparent().getparent().tag
            != "{http://www.w3.org/2001/XMLSchema}attribute"
        ):
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be restricted. Only elements, attributes, complexTypes and simpleTypes can be white-listed for instruction, "
                + restrictMethod
                + "."
            )

        else:

            matchedXpath = dict_path_elem[pathToRestrict]

            elems_to_keep = row.xpath("./Element/text()", namespaces=namespaces)
            attrs_to_keep = row.xpath("./Attribute/text()", namespaces=namespaces)
            enums_to_keep = row.xpath("./Enumeration/text()", namespaces=namespaces)
            blacklist_all_elem = row.xpath(
                "./@ExcludeAllElements|./@BlacklistAllElements", namespaces=namespaces
            )
            blacklist_all_attr = row.xpath(
                "./@ExcludeAllAttributes|./@BlacklistAllAttributes",
                namespaces=namespaces,
            )

            if attrs_to_keep == [] and enums_to_keep == [] and elems_to_keep == []:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be restricted. No element sub-items or enumerations specified to customise for instruction, "
                    + restrictMethod
                    + "."
                )

            if blacklist_all_elem != [] and blacklist_all_attr != []:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Customisation will leave Path '"
                    + pathToRestrict
                    + "' with no child items, please use Exclude customisation to remove the complete element in instruction, "
                    + restrictMethod
                    + "."
                )

            if blacklist_all_elem != [] and elems_to_keep != []:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "ExcludeAllElements flag can not be turned on for Path '"
                    + pathToRestrict
                    + "' as there are child elements to be included in instruction, "
                    + restrictMethod
                    + "."
                )

            if blacklist_all_attr != [] and attrs_to_keep != []:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "ExcludeAllAttributes flag can not be turned on for Path '"
                    + pathToRestrict
                    + "' as there are child attributes to be included in instruction, "
                    + restrictMethod
                    + "."
                )

            if attrs_to_keep != [] and enums_to_keep != []:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be restricted. Only element sub-items or enumerations can be specified in this instruction, "
                    + restrictMethod
                    + "."
                )

            if elems_to_keep != [] and enums_to_keep != []:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be restricted. Only element sub-items or enumerations can be specified in this instruction, "
                    + restrictMethod
                    + "."
                )

            if blacklist_all_attr == ["Yes"]:
                attrs_to_keep.append("IMPOSSIBLE STRING")

            if attrs_to_keep != []:

                attrs_to_keep = [pathToRestrict + "." + s for s in attrs_to_keep]

                parent = matchedXpath.getparent().getparent().getparent()
                child_attrs_to_loop = parent.xpath(
                    "./xs:complexType/xs:attribute/xs:annotation/xs:appinfo/lx:path/text()",
                    namespaces=namespaces,
                )
                if child_attrs_to_loop == []:
                    child_attrs_to_loop = parent.xpath(
                        "./xs:attribute/xs:annotation/xs:appinfo/lx:path/text()",
                        namespaces=namespaces,
                    )

                for dont_keep_path in child_attrs_to_loop:
                    if dont_keep_path not in attrs_to_keep:

                        newBlacklistPath = etree.Element("Path")
                        newBlacklistPath.text = dont_keep_path

                        newBlacklistItem = etree.Element("CustomiseItem")
                        newBlacklistItem.set("Exclude", "Yes")
                        newBlacklistItem.set("linenumber", linenum)
                        newBlacklistItem.append(newBlacklistPath)
                        newBlacklistItem.tail = "\n"

                        instruction_file_root.append(newBlacklistItem)

            if blacklist_all_elem == ["Yes"]:
                elems_to_keep.append("IMPOSSIBLE STRING")

            if elems_to_keep != []:

                elems_to_keep = [pathToRestrict + "." + s for s in elems_to_keep]

                parent = matchedXpath.getparent().getparent().getparent()

                child_elems_to_loop = parent.xpath(
                    "./xs:complexType/xs:sequence/xs:element/xs:annotation/xs:appinfo/lx:path/text()|./xs:complexType/xs:choice/xs:element/xs:annotation/xs:appinfo/lx:path/text()",
                    namespaces=namespaces,
                )
                if child_elems_to_loop == []:
                    child_elems_to_loop = parent.xpath(
                        "./xs:sequence/xs:element/xs:annotation/xs:appinfo/lx:path/text()|./xs:choice/xs:element/xs:annotation/xs:appinfo/lx:path/text() ",
                        namespaces=namespaces,
                    )

                for dont_keep_path in child_elems_to_loop:
                    if dont_keep_path not in elems_to_keep:

                        newBlacklistPath = etree.Element("Path")
                        newBlacklistPath.text = dont_keep_path

                        newBlacklistItem = etree.Element("CustomiseItem")
                        newBlacklistItem.set("Exclude", "Yes")
                        newBlacklistItem.set("linenumber", linenum)
                        newBlacklistItem.append(newBlacklistPath)
                        newBlacklistItem.tail = "\n"

                        instruction_file_root.append(newBlacklistItem)

            if enums_to_keep != []:

                parent = matchedXpath.getparent().getparent().getparent()

                if parent.tag == "{http://www.w3.org/2001/XMLSchema}simpleType":

                    enums_to_keep = [pathToRestrict + "." + s for s in enums_to_keep]

                    child_enums_to_loop = parent.xpath(
                        "./xs:restriction/xs:enumeration/xs:annotation/xs:appinfo/lx:path/text()",
                        namespaces=namespaces,
                    )

                    for dont_keep_path in child_enums_to_loop:
                        if dont_keep_path not in enums_to_keep:

                            newBlacklistPath = etree.Element("Path")
                            newBlacklistPath.text = dont_keep_path

                            newBlacklistItem = etree.Element("CustomiseItem")
                            newBlacklistItem.set("Exclude", "Yes")
                            newBlacklistItem.set("linenumber", linenum)
                            newBlacklistItem.append(newBlacklistPath)
                            newBlacklistItem.tail = "\n"

                            instruction_file_root.append(newBlacklistItem)

                elif parent.tag == "{http://www.w3.org/2001/XMLSchema}attribute":

                    ## first get all the schema enums from type and remove the ones not needed
                    if "type" in parent.attrib:
                        stype = parent.attrib["type"]
                        if "List" in stype:
                            if stype in dict_path_elem:
                                enumeration_to_modify = dict_path_elem[stype]

                                ## creating a new enum with only certain enums
                                new_enum = copy.deepcopy(
                                    enumeration_to_modify.getparent()
                                    .getparent()
                                    .getparent()
                                )  ## copy simpletype
                                cname = (
                                    "custom"
                                    + str(sequence)
                                    + parent.attrib["name"]
                                    + stype
                                )
                                new_enum.set("name", cname)

                                new_enum[0][0].text = cname
                                new_enum[0][1][0].text = cname
                                new_enum[0][1][1].text = cname

                                list_mark_for_deletion = []
                                for child in new_enum[1]:  ##simpleType/restriction
                                    if child.attrib["value"] not in enums_to_keep:
                                        list_mark_for_deletion.append(child)
                                    else:
                                        if "path" in child[0][1][0].tag:
                                            child[0][1][0].text = str(
                                                child[0][1][0].text
                                            ).replace(stype, cname)
                                        else:
                                            child[0][1][1].text = str(
                                                child[0][1][1].text
                                            ).replace(stype, cname)

                                for elem in list_mark_for_deletion:
                                    new_enum[1].remove(elem)

                                ##link it to this attribute
                                parent.attrib["type"] = cname
                                xmlParsedSchemaRoot.append(new_enum)
                            else:
                                warningList.append(
                                    "\n    Error On Line "
                                    + linenum
                                    + ": "
                                    + "Path '"
                                    + pathToRestrict
                                    + "' can not be found in schema for instruction, "
                                    + restrictMethod
                                    + "."
                                )
                        else:
                            warningList.append(
                                "\n    Error On Line "
                                + linenum
                                + ": "
                                + "Path '"
                                + pathToRestrict
                                + "' attribute does not have a valid referenced simple type can not be found in schema for instruction, "
                                + restrictMethod
                                + "."
                                "Include customisation for attribute does not have a valid referenced simple type: "
                                + pathToRestrict
                                + ", "
                                + restrictMethod
                            )
                    else:
                        warningList.append(
                            "\n    Error On Line "
                            + linenum
                            + ": "
                            + "Path '"
                            + pathToRestrict
                            + "' attribute does not have a valid referenced simple type for instruction, "
                            + restrictMethod
                            + "."
                        )

    restrictMethod = "Exclude"
    blacklist_paths = []
    blacklist_paths = blacklist_paths + instruction_file_root.findall(
        "CustomiseItem[@Exclude='Yes']/Path"
    )
    blacklist_paths = blacklist_paths + instruction_file_root.findall(
        "CustomiseItem[@Blacklist='Yes']/Path"
    )
    
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
        "Package.Instructions"
    ]    
    
    s = len(blacklist_paths)
    removed_blacklist_paths = []
    simpleandcomplex_paths = []
    countExcludePath = 2
    for row in blacklist_paths:  #
        pathToRestrict = row.text
        linenum = str(row.getparent().get("linenumber"))

        if pathToRestrict in paths_that_cant_removed:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be removed. LIXI reserved attributes can not be excluded for instruction, "
                + restrictMethod
                + "."
            )
        
        countExcludePath = countExcludePath + 1
        # find the Path Element that contains <lx:path>xxx</lx:path>
        if pathToRestrict not in dict_path_elem:
            # ----------------------------------------------------------------------------
            # We need to report a warning here that the script contains elements to
            # exclude that are not found
            # ----------------------------------------------------------------------------
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:
            matchedXpath = dict_path_elem[pathToRestrict]
            ##this is done to ensure no simpleType or complexType are deleted that have a dangling reference left to an unblacklisted
            if (
                matchedXpath.getparent().getparent().getparent().tag
                == "{http://www.w3.org/2001/XMLSchema}simpleType"
                or matchedXpath.getparent().getparent().getparent().tag
                == "{http://www.w3.org/2001/XMLSchema}complexType"
            ):
                # warningList.append('Types can not be explicitly blacklisted. The referencing attribute/element needs to be removed for a type to be removed. :'  + pathToRestrict + ', ' + restrictMethod)
                pass  # Don't delete it now let the second process run.
            else:

                enums_to_keep = row.getparent().xpath(
                    "./Enumeration/text()", namespaces=namespaces
                )

                if len(enums_to_keep) > 0:
                    parent = matchedXpath.getparent().getparent().getparent()
                    if parent.tag == "{http://www.w3.org/2001/XMLSchema}attribute":
                        ## first get all the schema enums from type and remove the ones not needed
                        if "type" in parent.attrib:
                            stype = parent.attrib["type"]
                            if "List" in stype:
                                if stype in dict_path_elem:
                                    enumeration_to_modify = dict_path_elem[stype]

                                    ## creating a new enum with only certain enums
                                    new_enum = copy.deepcopy(
                                        enumeration_to_modify.getparent()
                                        .getparent()
                                        .getparent()
                                    )  ## copy simpletype
                                    cname = (
                                        "custom"
                                        + str(sequence)
                                        + parent.attrib["name"]
                                        + stype
                                    )
                                    new_enum.set("name", cname)

                                    new_enum[0][0].text = cname
                                    new_enum[0][1][0].text = cname
                                    new_enum[0][1][1].text = cname

                                    list_mark_for_deletion = []
                                    for child in new_enum[1]:  ##simpleType/restriction
                                        if child.attrib["value"] in enums_to_keep:
                                            list_mark_for_deletion.append(child)
                                        else:
                                            if "path" in child[0][1][0].tag:
                                                child[0][1][0].text = str(
                                                    child[0][1][0].text
                                                ).replace(stype, cname)
                                            else:
                                                child[0][1][1].text = str(
                                                    child[0][1][1].text
                                                ).replace(stype, cname)

                                    for elem in list_mark_for_deletion:
                                        new_enum[1].remove(elem)

                                    ##link it to this attribute
                                    parent.attrib["type"] = cname
                                    xmlParsedSchemaRoot.append(new_enum)
                                else:
                                    warningList.append(
                                        "\n    Error On Line "
                                        + linenum
                                        + ": "
                                        + "Path '"
                                        + pathToRestrict
                                        + "' can not be found in schema for instruction, "
                                        + restrictMethod
                                        + "."
                                    )
                            else:
                                warningList.append(
                                    "\n    Error On Line "
                                    + linenum
                                    + ": "
                                    + "Path '"
                                    + pathToRestrict
                                    + "' attribute does not have a valid referenced simple type for instruction, "
                                    + restrictMethod
                                    + "."
                                )
                        else:
                            warningList.append(
                                "\n    Error On Line "
                                + linenum
                                + ": "
                                + "Path '"
                                + pathToRestrict
                                + "' attribute does not have a valid referenced simple type for instruction, "
                                + restrictMethod
                                + "."
                            )

                else:

                    elementToDelete = matchedXpath.getparent().getparent().getparent()

                    if "use" in elementToDelete.attrib:  # Attributes
                        if elementToDelete.attrib["use"] == "required":
                            check = any(
                                path.text in pathToRestrict[:-1]
                                for path in blacklist_paths
                            )
                            if check == False:  # Check signifies if parent was removed
                                warningList.append(
                                    "\n    Error On Line "
                                    + linenum
                                    + ": "
                                    + "Path '"
                                    + pathToRestrict
                                    + "' can not be removed. This attribute has 'use' set as required as per LIXI schema in instruction, "
                                    + restrictMethod
                                    + "."
                                )
                    elif "minOccurs" in elementToDelete.attrib:  # Elements
                        
                        if elementToDelete.attrib["minOccurs"] == "1":
                            if elementToDelete.getparent() != None:
                                
                                if (
                                    elementToDelete.getparent().tag
                                    == "{http://www.w3.org/2001/XMLSchema}choice"
                                ):
                                    if len(elementToDelete.getparent().getchildren()) < 2:
                                        warningList.append(
                                            "\n    Error On Line "
                                            + linenum
                                            + ": "
                                            + "Path '"
                                            + pathToRestrict
                                            + "' can not be removed. Removing this element would leave no required child elements for the parent choice element in instruction, "
                                            + restrictMethod
                                            + "."
                                        )
                                    else:
                                        children = elementToDelete.getparent().getchildren()
                                        
                                        child1 = children[0].xpath("./xs:annotation/xs:appinfo/lx:path", namespaces=namespaces)[0]
                                        child2 = children[1].xpath("./xs:annotation/xs:appinfo/lx:path", namespaces=namespaces)[0]
                                        check1 = False
                                        check2 = False
                                        
                                        for path in blacklist_paths:
                                            if path.text == child1.text:
                                                check1 = True
                                            
                                            if path.text == child2.text:
                                                check2 = True                                            
                                        
                                        if check1 and check2:
                                            
                                            warningList.append(
                                                "\n    Error On Line "
                                                + linenum
                                                + ": "
                                                + "Path '"
                                                + pathToRestrict
                                                + "' can not be removed as its sibling element is also marked for deletion. Removing this element would leave no required child elements for the parent choice element in instruction, "
                                                + restrictMethod
                                                + "."
                                            )
                                else:
                                    if len(elementToDelete.getparent().getchildren()) < 2:
                                        warningList.append(
                                            "\n    Error On Line "
                                            + linenum
                                            + ": "
                                            + "Path '"
                                            + pathToRestrict
                                            + "' can not be removed. Removing this element would leave no required child elements for the parent in instruction, "
                                            + restrictMethod
                                            + "."
                                        )
                                    else:
                                        warningList.append(
                                            "\n    Error On Line "
                                            + linenum
                                            + ": "
                                            + "Path '"
                                            + pathToRestrict
                                            + "' can not be removed as this attribute has 'minOccurs' set as '1'. Please remove the parent instead in instruction, "
                                            + restrictMethod
                                            + "."
                                        )                                    
                        
                    if elementToDelete.getparent() != None:             
                        elementToDelete.getparent().remove(elementToDelete)
                        removed_blacklist_paths.append(pathToRestrict)
                    else:
                        warningList.append(
                            "\n    Error On Line "
                            + linenum
                            + ": "
                            + "Path '"
                            + pathToRestrict
                            + "' is already removed. Please remove duplicate instruction, "
                            + restrictMethod
                            + "."
                        )                         

                    # xmlExcludePath.text = pathToRestrict
                    xmlExcludePath = etree.Element(
                        "{lixi.org.au/schema/appinfo_instructions}path"
                    )
                    xmlExcludePath.tail = "\n"
                    xmlExcludePath.text = pathToRestrict
                    xmlBlacklist.append(xmlExcludePath)

                    countExcludePath = countExcludePath + 1

    # Removing dangling simpleType and ComplexTypes paths
    referenced_type_xpath = xmlParsedSchemaRoot.xpath(
        "./xs:complexType|./xs:simpleType", namespaces=namespaces
    )  #
    all_referenced_type_xpath = xmlParsedSchemaRoot.xpath(
        "//xs:attribute/@type|//xs:element/@type", namespaces=namespaces
    )  #
    all_referenced_type_xpath = list(dict.fromkeys(all_referenced_type_xpath))

    for referenced_type in referenced_type_xpath:
        referenced_type_name = referenced_type.attrib["name"]

        # if no references remove it from schema
        if referenced_type_name not in all_referenced_type_xpath:
            # xmlExcludePath.text = pathToRestrict
            xmlExcludePath = etree.Element(
                "{lixi.org.au/schema/appinfo_instructions}path"
            )
            xmlExcludePath.tail = "\n"
            xmlExcludePath.text = referenced_type.xpath(
                "./xs:annotation/xs:appinfo/lx:path/text()", namespaces=namespaces
            )[0]
            xmlBlacklist.append(xmlExcludePath)

            countExcludePath = countExcludePath + 1

            # Remove the parent element (step up to AppInfo > Annotation > Parent Element )
            referenced_type.getparent().remove(referenced_type)
       

    # re-drawing a list of all path elems after blacklist
    dict_path_elem = {}
    all_schema_path_elements = xmlParsedSchemaRoot.xpath(
        "//lx:path", namespaces=namespaces
    )  #
    for path_elem in all_schema_path_elements:
        
        ##Remove all references to deleted element
        if len(path_elem.getparent().xpath("./lx:references/lx:target", namespaces=namespaces) ) >1:
            refs = path_elem.getparent().find("./lx:references", namespaces=namespaces)
            
            mark_for_del = []
            for ref_path in refs.findall("./lx:target", namespaces=namespaces):
                if ref_path.text in removed_blacklist_paths:
                    mark_for_del.append(ref_path)
            
            for i in range(0, len(mark_for_del)):
                refs.remove(mark_for_del[i])
        
        dict_path_elem[path_elem.text] = path_elem

    restrictMethod = "OptionalToMandatory"
    optional_to_mandatory_paths = instruction_file_root.findall(
        "CustomiseItem[@OptionalToMandatory='Yes']/Path"
    )
    for row in optional_to_mandatory_paths:
        linenum = str(row.getparent().get("linenumber"))
        pathToRestrict = row.text

        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:
            matchedXpath = dict_path_elem[pathToRestrict]

            xmlOptionalToMandatoryPath = etree.Element(
                "{lixi.org.au/schema/appinfo_instructions}path"
            )
            xmlOptionalToMandatoryPath.tail = "\n"
            xmlOptionalToMandatoryPath.text = pathToRestrict
            xmlOptionalToMandatory.append(xmlOptionalToMandatoryPath)

            countExcludePath = countExcludePath + 1

            if (
                matchedXpath.getparent().getparent().getparent().tag
                == "{http://www.w3.org/2001/XMLSchema}attribute"
            ):
                matchedXpath.getparent().getparent().getparent().attrib[
                    "use"
                ] = "required"
            else:
                matchedXpath.getparent().getparent().getparent().attrib[
                    "minOccurs"
                ] = "1"

    restrictMethod = "CustomMinOccurs"
    custom_min_occurs_paths = instruction_file_root.findall(
        "CustomiseItem[@CustomMinOccurs='Yes']"
    )
    for row in custom_min_occurs_paths:
        linenum = str(row.get("linenumber"))
        pathToRestrict = row.find("Path").text

        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:
            e = dict_path_elem[pathToRestrict]

            if (
                e.getparent().getparent().getparent().tag
                == "{http://www.w3.org/2001/XMLSchema}element"
            ):

                # checking if current value (either default or by setting OptionalToMandatory is greater)
                if e.getparent().getparent().getparent().attrib["minOccurs"] != None:
                    current_min_occurs = (
                        e.getparent().getparent().getparent().attrib["minOccurs"]
                    )
                else:
                    current_min_occurs = "1"

                new_min_occurs = row.find("CustomMinOccurs").text

                if new_min_occurs == "unbounded":
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. A custom minOccurs value can not be unbounded here for instruction, "
                        + restrictMethod
                        + "."
                    )

                elif int(current_min_occurs) > int(new_min_occurs):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. A custom minOccurs value can not be lower than the original value for instruction, "
                        + restrictMethod
                        + "."
                    )

                else:

                    xmlCustomMinOccursPath = etree.Element(
                        "{lixi.org.au/schema/appinfo_instructions}path"
                    )
                    xmlCustomMinOccursPath.tail = "\n"
                    xmlCustomMinOccursPath.text = pathToRestrict
                    xmlCustomMinOccurs.append(xmlCustomMinOccursPath)

                    e.getparent().getparent().getparent().attrib[
                        "minOccurs"
                    ] = new_min_occurs

            else:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. A custom minOccurs value can only be applied to an Element for instruction, "
                    + restrictMethod
                    + "."
                )

    restrictMethod = "CustomMaxOccurs"
    custom_max_occurs_paths = instruction_file_root.findall(
        "CustomiseItem[@CustomMaxOccurs='Yes']"
    )
    for row in custom_max_occurs_paths:
        linenum = str(row.get("linenumber"))
        pathToRestrict = row.find("Path").text

        # find the Path Element that contains <lx:path>xxx</lx:path>
        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:
            e = dict_path_elem[pathToRestrict]

            if (
                e.getparent().getparent().getparent().tag
                == "{http://www.w3.org/2001/XMLSchema}element"
            ):

                # checking if current value (either default or by setting OptionalToMandatory is greater)
                if e.getparent().getparent().getparent().attrib["maxOccurs"] != None:
                    current_max_occurs = (
                        e.getparent().getparent().getparent().attrib["maxOccurs"]
                    )
                else:
                    current_max_occurs = "1"

                new_max_occurs = row.find("CustomMaxOccurs").text

                if new_max_occurs == "0":
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. A custom maxOccurs value can not be '0' for instruction, "
                        + restrictMethod
                        + "."
                    )

                else:

                    if current_max_occurs == "unbounded":
                        xmlCustomMaxOccursPath = etree.Element(
                            "{lixi.org.au/schema/appinfo_instructions}path"
                        )
                        xmlCustomMaxOccursPath.tail = "\n"
                        xmlCustomMaxOccursPath.text = pathToRestrict
                        xmlCustomMaxOccurs.append(xmlCustomMaxOccursPath)

                        e.getparent().getparent().getparent().attrib[
                            "maxOccurs"
                        ] = new_max_occurs
                    else:
                        if int(current_max_occurs) < int(new_max_occurs):
                            warningList.append(
                                "\n    Error On Line "
                                + linenum
                                + ": "
                                + "Path '"
                                + pathToRestrict
                                + "' can not be customised. A custom maxOccurs value can not be higher than the original value for instruction, "
                                + restrictMethod
                                + "."
                            )
                        else:
                            xmlCustomMaxOccursPath = etree.Element(
                                "{lixi.org.au/schema/appinfo_instructions}path"
                            )
                            xmlCustomMaxOccursPath.tail = "\n"
                            xmlCustomMaxOccursPath.text = pathToRestrict
                            xmlCustomMaxOccurs.append(xmlCustomMaxOccursPath)

                            e.getparent().getparent().getparent().attrib[
                                "maxOccurs"
                            ] = new_max_occurs

            else:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. A custom maxOccurs value can only be applied to an Element for instruction, "
                    + restrictMethod
                    + "."
                )

    restrictMethod = "StringToList"
    string_to_enum_elements = instruction_file_root.findall(
        "CustomiseItem[@StringToList='Yes']"
    )
    for elem in string_to_enum_elements:
        linenum = str(row.get("linenumber"))
        pathToRestrict = elem.find("Path").text

        # find the Path Element that contains <lx:path>xxx</lx:path>
        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:

            e = dict_path_elem[pathToRestrict]

            xmlStringToEnumPath = etree.Element(
                "{lixi.org.au/schema/appinfo_instructions}path"
            )
            xmlStringToEnumPath.tail = "\n"
            xmlStringToEnumPath.text = pathToRestrict
            xmlStringToEnum.append(xmlStringToEnumPath)

            if (
                e.getparent().getparent().getparent().tag
                != "{http://www.w3.org/2001/XMLSchema}attribute"
            ):
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. Only attributes can be specified for instruction, "
                    + restrictMethod
                    + "."
                )

            elif e.getparent().getparent().getparent().attrib["type"] != "stringType":
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. Only stringType can be specified for instruction, "
                    + restrictMethod
                    + "."
                )

            else:

                custom_name = (
                    "custom"
                    + str(sequence)
                    + e.getparent().getparent().getparent().attrib["name"]
                    + "List"
                )
                e.getparent().getparent().getparent().attrib["type"] = custom_name

                xssimpleType = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}simpleType"
                )

                xsannotation = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}annotation"
                )
                xsannotation.tail = "\n"
                xsdocumentation = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}documentation"
                )
                xsdocumentation.tail = "\n"
                xsappinfo = etree.Element("{http://www.w3.org/2001/XMLSchema}appinfo")
                xsappinfo.tail = "\n"
                lxpath = etree.Element("{lixi.org.au/schema/appinfo_elements}path")
                lxpath.tail = "\n"
                lxlabel = etree.Element("{lixi.org.au/schema/appinfo_elements}label")
                lxlabel.tail = "\n"
                xsrestriction = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}restriction"
                )
                xsrestriction.tail = "\n"

                for enum_elem in elem.findall("Enumeration"):

                    txsenumeration = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}enumeration"
                    )
                    txsenumeration.text = "\n"
                    txsenumeration.tail = "\n"
                    txsannotation = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}annotation"
                    )
                    txsannotation.tail = "\n"
                    txsdocumentation = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}documentation"
                    )
                    txsdocumentation.tail = "\n"
                    txsappinfo = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}appinfo"
                    )
                    txsappinfo.tail = "\n"
                    tlxpath = etree.Element("{lixi.org.au/schema/appinfo_elements}path")
                    tlxpath.tail = "\n"
                    tlxlabel = etree.Element(
                        "{lixi.org.au/schema/appinfo_elements}label"
                    )
                    tlxlabel.tail = "\n"

                    tlxlabel.text = enum_elem.text
                    tlxpath.text = custom_name + "." + enum_elem.text
                    txsappinfo.append(tlxpath)
                    txsappinfo.append(tlxlabel)
                    if "Definition" in enum_elem.attrib:
                        txsdocumentation.text = enum_elem.get("Definition")
                    else:
                        txsdocumentation.text = enum_elem.text
                    txsannotation.append(txsdocumentation)
                    txsannotation.append(txsappinfo)
                    txsenumeration.set("value", enum_elem.text)
                    txsenumeration.append(txsannotation)

                    xsrestriction.append(txsenumeration)

                xsrestriction.set("base", "xs:token")
                lxlabel.text = custom_name
                lxpath.text = custom_name
                xsappinfo.append(lxpath)
                xsappinfo.append(lxlabel)
                xsdocumentation.text = (
                    elem.find("CustomDocumentation").text
                    if elem.find("CustomDocumentation") != None
                    else custom_name
                )
                xsannotation.append(xsdocumentation)
                xsannotation.append(xsappinfo)
                xssimpleType.set("name", custom_name)
                xssimpleType.append(xsannotation)
                xssimpleType.append(xsrestriction)

                xmlParsedSchemaRoot.append(xssimpleType)

                sequence = sequence + 1

    restrictMethod = "StringToPattern"
    string_to_pattern_paths = instruction_file_root.findall(
        "CustomiseItem[@StringToPattern='Yes']"
    )
    for elem in string_to_pattern_paths:
        linenum = str(row.get("linenumber"))
        pathToRestrict = elem.find("Path").text

        # find the Path Element that contains <lx:path>xxx</lx:path>
        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:

            if elem.find("Enumeration") != None:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. Instruction can not have both a custom pattern and custom enumeration for instruction, "
                    + restrictMethod
                    + "."
                )
            else:

                e = dict_path_elem[pathToRestrict]

                xmlStringToPatternPath = etree.Element(
                    "{lixi.org.au/schema/appinfo_instructions}path"
                )
                xmlStringToPatternPath.tail = "\n"
                xmlStringToPatternPath.text = pathToRestrict
                xmlStringToPattern.append(xmlStringToPatternPath)

                if (
                    e.getparent().getparent().getparent().tag
                    != "{http://www.w3.org/2001/XMLSchema}attribute"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Only attributes can be specified for instruction, "
                        + restrictMethod
                        + "."
                    )

                elif (
                    e.getparent().getparent().getparent().attrib["type"] != "stringType"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Only stringType can be specified for instruction, "
                        + restrictMethod
                        + "."
                    )

                else:

                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Pattern"
                    )
                    e.getparent().getparent().getparent().attrib["type"] = custom_name

                    xssimpleType = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}simpleType"
                    )
                    xsannotation = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}annotation"
                    )
                    xsannotation.tail = "\n"
                    xsdocumentation = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}documentation"
                    )
                    xsdocumentation.tail = "\n"
                    xsappinfo = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}appinfo"
                    )
                    xsappinfo.tail = "\n"
                    lxpath = etree.Element("{lixi.org.au/schema/appinfo_elements}path")
                    lxpath.tail = "\n"
                    lxlabel = etree.Element(
                        "{lixi.org.au/schema/appinfo_elements}label"
                    )
                    lxlabel.tail = "\n"
                    xsrestriction = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}restriction"
                    )
                    xsrestriction.tail = "\n"
                    xspattern = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}pattern"
                    )
                    xspattern.tail = "\n"

                    xspattern.set("value", elem.find("Pattern").text)
                    xsrestriction.append(xspattern)
                    xsrestriction.set("base", "xs:string")
                    lxlabel.text = custom_name
                    lxpath.text = custom_name
                    xsappinfo.append(lxpath)
                    xsappinfo.append(lxlabel)
                    xsdocumentation.text = (
                        elem.find("CustomDocumentation").text
                        if elem.find("CustomDocumentation") != None
                        else custom_name
                    )
                    xsannotation.append(xsdocumentation)
                    xsannotation.append(xsappinfo)
                    xssimpleType.set("name", custom_name)
                    xssimpleType.append(xsannotation)
                    xssimpleType.append(xsrestriction)

                    xmlParsedSchemaRoot.append(xssimpleType)

                    sequence = sequence + 1

    restrictMethod = "CustomRange"
    range_paths = instruction_file_root.xpath(
        "./CustomiseItem[@CustomCurrencyRange='Yes']|./CustomiseItem[@CustomDateTimeRange='Yes']|./CustomiseItem[@CustomDateRange='Yes']|./CustomiseItem[@CustomDecimalRange='Yes']|./CustomiseItem[@CustomYearRange='Yes']|./CustomiseItem[@CustomIntegerRange='Yes']|./CustomiseItem[@CustomPercentageRange='Yes']"
    )
    for elem in range_paths:
        linenum = str(row.get("linenumber"))
        pathToRestrict = elem.find("Path").text

        # find the Path Element that contains <lx:path>xxx</lx:path>
        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:

            e = dict_path_elem[pathToRestrict]
            check = False
            custom_name = None
            att_type = None
            att_min = None
            att_max = None

            custRange = etree.Element("{lixi.org.au/schema/appinfo_instructions}path")
            custRange.tail = "\n"
            custRange.text = pathToRestrict

            if elem.find("Enumeration") != None:
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. Instruction can not have both a custom range and custom enumeration for instruction, "
                    + restrictMethod
                    + "."
                )
            elif (
                e.getparent().getparent().getparent().tag
                != "{http://www.w3.org/2001/XMLSchema}attribute"
            ):
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. Only attributes can be specified for instruction, "
                    + restrictMethod
                    + "."
                )
            elif e.getparent().getparent().getparent().attrib["type"] == "stringType":
                warningList.append(
                    "\n    Error On Line "
                    + linenum
                    + ": "
                    + "Path '"
                    + pathToRestrict
                    + "' can not be customised. stringType can not be specified for instruction, "
                    + restrictMethod
                    + "."
                )
            elif "CustomCurrencyRange" in elem.attrib:
                if (
                    e.getparent().getparent().getparent().attrib["type"]
                    != "currencyType"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. CustomCurrencyRange cannot be specified for an attribute that is not an integer for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinCurrency|./MaxCurrency")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomCurrencyRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinInteger|./MaxInteger|./MinDateTime|./MaxDateTime|./MinDate|./MaxDate|./MinDecimal|./MaxDecimal|./MinYear|./MaxYear|./MinPercentage|./MaxPercentage|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomCurrencyRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomCurrencyRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:decimal"
                    att_min = (
                        elem.find("MinCurrency").text
                        if elem.find("MinCurrency") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxCurrency").text
                        if elem.find("MaxCurrency") != None
                        else None
                    )
            elif "CustomDateTimeRange" in elem.attrib:
                if (
                    e.getparent().getparent().getparent().attrib["type"]
                    != "dateTimeType"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. CustomDateTimeRange cannot be specified for an attribute that is not a dateTimeType for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinDateTime|./MaxDateTime")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomDateTimeRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinCurrency|./MaxCurrency|./MinInteger|./MaxInteger|./MinDate|./MaxDate|./MinDecimal|./MaxDecimal|./MinYear|./MaxYear|./MinPercentage|./MaxPercentage|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomDateTimeRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomDateTimeRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:dateTime"
                    att_min = (
                        elem.find("MinDateTime").text
                        if elem.find("MinDateTime") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxDateTime").text
                        if elem.find("MaxDateTime") != None
                        else None
                    )
            elif "CustomDateRange" in elem.attrib:
                if e.getparent().getparent().getparent().attrib["type"] != "dateType":
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. CustomDateRange cannot be specified for an attribute that is not a dateType for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinDate|./MaxDate")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomDateRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinCurrency|./MaxCurrency|./MinDateTime|./MaxDateTime|./MinInteger|./MaxInteger|./MinDecimal|./MaxDecimal|./MinYear|./MaxYear|./MinPercentage|./MaxPercentage|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomDateRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomDateRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:date"
                    att_min = (
                        elem.find("MinDate").text
                        if elem.find("MinDate") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxDate").text
                        if elem.find("MaxDate") != None
                        else None
                    )
            elif "CustomDecimalRange" in elem.attrib:
                if (
                    e.getparent().getparent().getparent().attrib["type"]
                    != "decimalType"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customisCustomDecimalRange cannot be specified for an attribute that is not a decimalType for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinDecimal|./MaxDecimal")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomDecimalRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinCurrency|./MaxCurrency|./MinDateTime|./MaxDateTime|./MinDate|./MaxDate|./MinInteger|./MaxInteger|./MinYear|./MaxYear|./MinPercentage|./MaxPercentage|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomDecimalRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomDecimalRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:decimal"
                    att_min = (
                        elem.find("MinDecimal").text
                        if elem.find("MinDecimal") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxDecimal").text
                        if elem.find("MaxDecimal") != None
                        else None
                    )
            elif "CustomYearRange" in elem.attrib:
                if e.getparent().getparent().getparent().attrib["type"] != "gYearType":
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. CustomYearRange cannot be specified for an attribute that is not a gYearType for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinYear|./MaxYear")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomYearRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinCurrency|./MaxCurrency|./MinDateTime|./MaxDateTime|./MinDate|./MaxDate|./MinDecimal|./MaxDecimal|./MinInteger|./MaxInteger|./MinPercentage|./MaxPercentage|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomYearRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomYearRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:gYear"
                    att_min = (
                        elem.find("MinYear").text
                        if elem.find("MinYear") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxYear").text
                        if elem.find("MaxYear") != None
                        else None
                    )
            elif "CustomIntegerRange" in elem.attrib:
                if (
                    e.getparent().getparent().getparent().attrib["type"]
                    != "integerType"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. CustomIntegerRange cannot be specified for an attribute that is not an integer for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinInteger|./MaxInteger")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomIntegerRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinCurrency|./MaxCurrency|./MinDateTime|./MaxDateTime|./MinDate|./MaxDate|./MinDecimal|./MaxDecimal|./MinYear|./MaxYear|./MinPercentage|./MaxPercentage|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomIntegerRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomIntegerRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:integer"
                    att_min = (
                        elem.find("MinInteger").text
                        if elem.find("MinInteger") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxInteger").text
                        if elem.find("MaxInteger") != None
                        else None
                    )
            elif "CustomPercentageRange" in elem.attrib:
                if (
                    e.getparent().getparent().getparent().attrib["type"]
                    != "percentType"
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. CustomPercentageRange cannot be specified for an attribute that is not a percentType for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif len(elem.xpath("./MinPercentage|./MaxPercentage")) == 0:
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Minimum and Maximum ranges not specified in CustomPercentageRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                elif (
                    len(
                        elem.xpath(
                            "./MinCurrency|./MaxCurrency|./MinDateTime|./MaxDateTime|./MinDate|./MaxDate|./MinDecimal|./MaxDecimal|./MinYear|./MaxYear|./MinInteger|./MaxInteger|"
                        )
                    )
                    != 0
                ):
                    warningList.append(
                        "\n    Error On Line "
                        + linenum
                        + ": "
                        + "Path '"
                        + pathToRestrict
                        + "' can not be customised. Invalid range type specified in CustomPercentageRange for instruction, "
                        + restrictMethod
                        + "."
                    )
                else:
                    check = True
                    xmlCustomPercentageRange.append(custRange)
                    custom_name = (
                        "custom"
                        + str(sequence)
                        + e.getparent().getparent().getparent().attrib["name"]
                        + "Range"
                    )
                    att_type = "xs:decimal"
                    att_min = (
                        elem.find("MinPercentage").text
                        if elem.find("MinPercentage") != None
                        else None
                    )
                    att_max = (
                        elem.find("MaxPercentage").text
                        if elem.find("MaxPercentage") != None
                        else None
                    )

            if check:
                e.getparent().getparent().getparent().attrib["type"] = custom_name

                xssimpleType = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}simpleType"
                )
                xsannotation = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}annotation"
                )
                xsannotation.tail = "\n"
                xsdocumentation = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}documentation"
                )
                xsdocumentation.tail = "\n"
                xsappinfo = etree.Element("{http://www.w3.org/2001/XMLSchema}appinfo")
                xsappinfo.tail = "\n"
                lxpath = etree.Element("{lixi.org.au/schema/appinfo_elements}path")
                lxpath.tail = "\n"
                lxlabel = etree.Element("{lixi.org.au/schema/appinfo_elements}label")
                lxlabel.tail = "\n"
                xsrestriction = etree.Element(
                    "{http://www.w3.org/2001/XMLSchema}restriction"
                )
                xsrestriction.tail = "\n"

                if att_min != None:
                    xspattern = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}minInclusive"
                    )
                    xspattern.tail = "\n"
                    xspattern.set("value", att_min)
                    xsrestriction.append(xspattern)

                if att_max != None:
                    xspattern = etree.Element(
                        "{http://www.w3.org/2001/XMLSchema}maxInclusive"
                    )
                    xspattern.tail = "\n"
                    xspattern.set("value", att_max)
                    xsrestriction.append(xspattern)

                xsrestriction.set("base", att_type)
                lxlabel.text = custom_name
                lxpath.text = custom_name
                xsappinfo.append(lxpath)
                xsappinfo.append(lxlabel)
                xsdocumentation.text = (
                    elem.find("CustomDocumentation").text
                    if elem.find("CustomDocumentation") != None
                    else custom_name
                )
                xsannotation.append(xsdocumentation)
                xsannotation.append(xsappinfo)
                xssimpleType.set("name", custom_name)
                xssimpleType.append(xsannotation)
                xssimpleType.append(xsrestriction)

                xmlParsedSchemaRoot.append(xssimpleType)

                sequence = sequence + 1

    customdocumentation = instruction_file_root.findall(
        "CustomiseItem/CustomDocumentation"
    )
    # set the heading for the custom documentation section
    customHeading = "Custom Documentation"

    # check the customHeading element
    custom_heading_instructions = instruction_file_root.xpath(
        "/Customisations", namespaces=namespaces
    )[0]
    if "CustomHeading" in custom_heading_instructions.attrib:
        customHeading = custom_heading_instructions.attrib["CustomHeading"]
    elif "customHeading" in custom_heading_instructions.attrib:
        customHeading = custom_heading_instructions.attrib["customHeading"]

    restrictMethod = "CustomDocumentation"
    for row in customdocumentation:
        linenum = str(row.getparent().get("linenumber"))
        # custom_documentation = row.find("CustomDocumentation").text
        custom_documentation = row.text
        pathToRestrict = row.getparent().find("Path").text

        # get the value of the customHeading attribute for this item
        if "CustomHeading" in row.getparent().attrib:
            customHeadingLocal = row.getparent().attrib["CustomHeading"]
            custom_documentation = (
                "#### " + customHeadingLocal + " \n\n" + custom_documentation
            )
        elif "customHeading" in row.getparent().attrib:
            customHeadingLocal = row.getparent().attrib["customHeading"]
            custom_documentation = (
                "#### " + customHeadingLocal + " \n\n" + custom_documentation
            )            
        else:
            custom_documentation = (
                "#### " + customHeading + " \n\n" + custom_documentation
            )

        # find the Path Element that contains <lx:path>xxx</lx:path>
        if pathToRestrict not in dict_path_elem:
            warningList.append(
                "\n    Error On Line "
                + linenum
                + ": "
                + "Path '"
                + pathToRestrict
                + "' can not be found in schema for instruction, "
                + restrictMethod
                + "."
            )

        else:

            e = dict_path_elem[pathToRestrict]

            xmlCustomDocumentation = etree.Element(
                "{lixi.org.au/schema/appinfo_elements}CustomDocumentation"
            )
            xmlCustomDocumentation.tail = "\n"
            xmlCustomDocumentation.text = custom_documentation

            e.getparent().insert(10, xmlCustomDocumentation)

            customexcerpt = row.getparent().find("CustomExcerpt")
            if customexcerpt != None:
                custom_excerpt = customexcerpt.text

                xmlCustomExcerpt = etree.Element(
                    "{lixi.org.au/schema/appinfo_elements}CustomExcerpt"
                )
                xmlCustomExcerpt.tail = "\n"
                xmlCustomExcerpt.text = custom_excerpt

                e.getparent().insert(11, xmlCustomExcerpt)

    if len(warningList) > 0:
        error = "Customised schema generation failed. Instructions are not correct.\n"
        error = error + "\nIncorrect Instructions:"
        for warning in warningList:
            error = error + warning
        raise LIXIValidationError(error)

    # get it into the correct indentation
    schema_str = etree.tostring(xmlParsedSchemaRoot).decode()
    schema_str = schema_str.strip().replace(">\n", ">").replace("\n<", "<")
    reparsed = dome.parseString(schema_str)
    astr = reparsed.toprettyxml(indent="  ")
    xmlParsedSchemaRoot = etree.fromstring(astr)
    
    
    # Removing dangling simpleType and ComplexTypes paths
    referenced_type_xpath = xmlParsedSchemaRoot.xpath(
        "./xs:complexType|./xs:simpleType", namespaces=namespaces
    )  #
    all_referenced_type_xpath = xmlParsedSchemaRoot.xpath(
        "//xs:attribute/@type|//xs:element/@type", namespaces=namespaces
    )  #
    all_referenced_type_xpath = list(dict.fromkeys(all_referenced_type_xpath))

    for referenced_type in referenced_type_xpath:
        referenced_type_name = referenced_type.attrib["name"]

        # if no references remove it from schema
        if referenced_type_name not in all_referenced_type_xpath:
            # xmlExcludePath.text = pathToRestrict
            xmlExcludePath = etree.Element(
                "{lixi.org.au/schema/appinfo_instructions}path"
            )
            xmlExcludePath.tail = "\n"
            xmlExcludePath.text = referenced_type.xpath(
                "./xs:annotation/xs:appinfo/lx:path/text()", namespaces=namespaces
            )[0]
            xmlBlacklist.append(xmlExcludePath)

            countExcludePath = countExcludePath + 1

            # Remove the parent element (step up to AppInfo > Annotation > Parent Element )
            referenced_type.getparent().remove(referenced_type)
            
    
    # Removing dangling simpleType and ComplexTypes paths
    referenced_type_xpath = xmlParsedSchemaRoot.xpath(
        "./xs:complexType|./xs:simpleType", namespaces=namespaces
    )  #
    all_referenced_type_xpath = xmlParsedSchemaRoot.xpath(
        "//xs:attribute/@type|//xs:element/@type", namespaces=namespaces
    )  #
    all_referenced_type_xpath = list(dict.fromkeys(all_referenced_type_xpath))

    for referenced_type in referenced_type_xpath:
        referenced_type_name = referenced_type.attrib["name"]

        # if no references remove it from schema
        if referenced_type_name not in all_referenced_type_xpath:
            # xmlExcludePath.text = pathToRestrict
            xmlExcludePath = etree.Element(
                "{lixi.org.au/schema/appinfo_instructions}path"
            )
            xmlExcludePath.tail = "\n"
            xmlExcludePath.text = referenced_type.xpath(
                "./xs:annotation/xs:appinfo/lx:path/text()", namespaces=namespaces
            )[0]
            xmlBlacklist.append(xmlExcludePath)

            countExcludePath = countExcludePath + 1

            # Remove the parent element (step up to AppInfo > Annotation > Parent Element )
            referenced_type.getparent().remove(referenced_type)            
    
    elems = xmlParsedSchemaRoot.xpath(
        "//xs:element|//xs:attribute", namespaces=namespaces
    )
    keys_map = {
        v: i
        for i, v in enumerate(
            ["name", "type", "minOccurs", "maxOccurs", "use", "fixed"]
        )
    }

    for elem in elems:
        keys = elem.attrib
        hey = dict(sorted(keys.items(), key=lambda pair: keys_map[pair[0]]))
        elem.attrib.clear()
        elem.attrib.update(hey)

    return xmlParsedSchemaRoot


def validate_instructions_set(instructions):
    """
    Validate the customization restrictions xml.

    Args:
        instructions (:obj:`lxml.etree`, required): Customization instructions provided as a Python etree.
            
    Returns:
        A string of blacklist customization restrictions xml that can be utilized by this library to generate a custom schema.
        
    Raises:
        LIXIValidationError: Validation errors in the file.
        
    """

    # Validate Custom Ins
    with io.open(
        pkg_resources.resource_filename(__name__, "customization.xsd"),
        "r",
        encoding="utf-8",
    ) as xsd_file_data:
        customisation_instructions_schema_doc = etree.parse(xsd_file_data)
    customisation_instructions_schema = etree.XMLSchema(
        customisation_instructions_schema_doc
    )
    valid = customisation_instructions_schema.validate(instructions)

    if valid:
        pass
    else:
        error = "Customised schema generation failed. Instructions file is not valid.\n"
        error = error + "\nInvalid Assertions:"

        for scerror in customisation_instructions_schema.error_log:
            error = (
                error
                + "\n    Error On Line "
                + str(scerror.line)
                + ": "
                + scerror.message
                + "."
            )

        raise LIXIValidationError(error)


def execute_customisation_instructions(schema_etree, instructions, output_name=None):
    """
    Generates a string of blacklist customization restrictions xml for a customized LIXI schema.

    Args:
        schema_etree (:obj:`lxml.etree`, required): LIXI schema provided as Python Etree.
        instructions (:obj:`str`, required): Customization instructions provided as a string. Defaults to None.
        output_name (:obj:`str`, optional): Custom schema name used in namespace. Defaults to None.
            
    Returns:
        customised_Schema_Annotated (str): A string of blacklist customization restrictions xml that can be utilized by this library to generate a custom schema.
        output_name (str): Custom schema name used in namespace. Used as a file name for the generated schema.
    """

    # Define the namespaces to be used and pre-set values to be used.
    lixi_schema_namespaces = {
        "xs": "http://www.w3.org/2001/XMLSchema",
        "lx": "lixi.org.au/schema/appinfo_elements",
        "li": "lixi.org.au/schema/appinfo_instructions",
    }
    parser = etree.XMLParser(remove_blank_text=True)

    transaction_schema_to_customise = copy.deepcopy(schema_etree)

    schema_transaction_type = transaction_schema_to_customise.xpath(
        './xs:element/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXITransactionType"]',
        namespaces=lixi_schema_namespaces,
    )[0]
    schema_transaction_type = schema_transaction_type.attrib["fixed"]

    schema_version = transaction_schema_to_customise.xpath(
        './xs:element/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXIVersion"]',
        namespaces=lixi_schema_namespaces,
    )[0]
    schema_version = schema_version.attrib["fixed"]

    master_schema_version = transaction_schema_to_customise.xpath(
        "./xs:annotation/xs:appinfo/lx:schemadetail", namespaces=lixi_schema_namespaces
    )[0]
    master_schema_version = master_schema_version.attrib["masterschemasource"]

    customisation_instructions = etree.fromstring(instructions, parser)
    validate_instructions_set(customisation_instructions)

    short_datetime_string = datetime.strftime(datetime.now(), "%Y_%m_%d-%H_%M")
    try:
        customisation_code = customisation_instructions.attrib["CustomisationCode"]
    except:
        customisation_code = "DEMO"

    try:
        lixi_code = customisation_instructions.attrib["LIXICode"]
    except:
        lixi_code = "LIXILIXI"

    lixi_custom_version_code = (
        "LIXI-"
        + schema_transaction_type
        + "-Custom-"
        + lixi_code
        + "-"
        + customisation_code
        + "-"
        + short_datetime_string
    )

    
    if output_name == None:
        output_name = lixi_custom_version_code
    else:
        if output_name.isspace():
            raise LIXIValidationError('Customised schema generation failed. Output name can not be just spaces.')        
        
        lixi_custom_version_code = output_name

    schema_documentation_text_annotated = (
        "This schema ("
        + lixi_custom_version_code
        + ".xsd) is a customised schema (by restriction) from "
        + schema_transaction_type
        + " "
        + schema_version
        + ", a sub-schema derived from the LIXI Master Schema ("
        + master_schema_version
        + ") that includes the annotation documentation."
    )

    # Generate schema
    customised_Schema_Annotated = CustomiseSingleSchema(
        transaction_schema_to_customise,
        customisation_instructions,
        schema_documentation_text_annotated,
        lixi_custom_version_code,
        lixi_schema_namespaces,
    )

    customised_Schema_Annotated = etree.tostring(
        customised_Schema_Annotated, pretty_print=True, encoding="UTF-8"
    ).decode("utf-8")

    return customised_Schema_Annotated, output_name
