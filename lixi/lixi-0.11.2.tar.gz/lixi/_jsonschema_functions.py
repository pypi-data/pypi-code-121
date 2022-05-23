from jsonschema import Draft4Validator, FormatChecker, exceptions
from collections import deque, OrderedDict
import isodate, datetime, json, copy, io
from lxml import etree

##
ns = {
    "xs": "http://www.w3.org/2001/XMLSchema",
    "lx": "lixi.org.au/schema/appinfo_elements",
    "li": "lixi.org.au/schema/appinfo_instructions",
}

xs = "http://www.w3.org/2001/XMLSchema"
lx = "lixi.org.au/schema/appinfo_elements"
li = "lixi.org.au/schema/appinfo_instructions"


class LIXIValidationError(Exception):
    def __init__(self, message, message_instance=None):
        super().__init__(message)
        self.message_instance = message_instance


def validate_json(json_message, json_schema):
    """Validates a LIXI JSON message against a LIXI JSON schema. Not used currently.
    
    Args:
        json_message (:obj:`dict`, required): A python message dict.  
        json_schema (:obj:`dict`, required): A python schema dict.
    
    Result:
        is_valid: True or False.
        validation_message: A short description of the validation message.
    
    Raises:
        ValidationError: Validation errors for the xml file.
    """

    counter = 1
    out_string = ""

    IDs = []
    IDREFs = []
    custom_format_checker = FormatChecker()
    idref_is_true = True

    @custom_format_checker.checks("lixi-year", exceptions.ValidationError)
    def format_year(string_value):
        try:
            dt = datetime.datetime.strptime(string_value, "%Y")
            return True
        except ValueError as e:
            raise exceptions.ValidationError(
                "'" + string_value + "' is not a valid year"
            )

    @custom_format_checker.checks("lixi-fulldate", exceptions.ValidationError)
    def format_fullyear(string_value):
        try:
            dt = datetime.datetime.strptime(string_value, "%Y-%m-%d")
            return True
        except ValueError as e:
            raise exceptions.ValidationError(
                "'" + string_value + "' is not a valid date"
            )

    @custom_format_checker.checks("lixi-datetime", exceptions.ValidationError)
    def format_datetime(string_value):
        try:
            dt = isodate.parse_datetime(string_value)
            return True
        except ValueError as e:
            raise exceptions.ValidationError(
                "'" + string_value + "' is not a valid ISO date string"
            )

    @custom_format_checker.checks("lixi-ID", exceptions.ValidationError)
    def format_ID(string_value):

        if string_value in IDs:
            raise exceptions.ValidationError("ID '" + string_value + "' is not unique")

        IDs.append(string_value)
        return True

    @custom_format_checker.checks("lixi-IDREF")
    def format_ID(string_value):
        IDREFs.append(string_value)
        return True

    def print_nested_error(error, old_path_list):
        path_list = deque()
        if isinstance(error, exceptions.ValidationError):
            if len(error.context) == 0:
                if isinstance(path_list, deque) and isinstance(error.path, deque):
                    path_list.extend(old_path_list)
                    path_list.extend(error.path)

                result_path = (
                    repr(path_list)
                    .replace("deque(['", "")
                    .replace("'])", "")
                    .replace("', '", ".")
                )
                out_string += (
                    "\nERROR "
                    + repr(counter)
                    + ": "
                    + error.message
                    + "\n  PATH: "
                    + result_path
                )
                counter += 1
            else:
                if isinstance(path_list, deque) and isinstance(error.path, deque):
                    path_list.extend(old_path_list)
                    path_list.extend(error.path)

                for child_error in error.context:
                    print_nested_error(child_error, path_list)

    validator = Draft4Validator(json_schema, format_checker=custom_format_checker)

    if validator.is_valid(json_message):

        for idref in IDREFs:
            if idref not in IDs:
                idref_is_true = False

        if idref_is_true:
            return True, "Message is Valid"
        else:
            out_string += "\n-> Message is Invalid"
            for idref in IDREFs:
                check = False
                if idref not in IDs:
                    check = True
                if check:
                    out_string += (
                        "\nERROR "
                        + repr(counter)
                        + ": IDREF '"
                        + idref
                        + "' does not have a referenced ID, PATH: Message-wide"
                    )
                counter += 1

            return False, out_string

    else:
        out_string += "\n-> Message is Invalid"

        message_errors = []
        message_errors = validator.iter_errors(json_message)

        for error in message_errors:
            path_list = deque()
            print_nested_error(error, path_list)

        for idref in IDREFs:
            check = False
            if idref not in IDs:
                check = True
            if check:
                out_string += (
                    "\nERROR "
                    + repr(counter)
                    + ": IDREF '"
                    + idref
                    + "' does not have a referenced ID, PATH: Message-wide"
                )
            counter += 1

        return False, out_string


def convert_to_json_schema_string(xmlstring):
    """Converts a LIXI XML schema to JSON schema.
    
    Args: 
        xml_schema (:obj:`str`, required):  A lxml etree LIXI schema.
    
    Result:
        A json LIXI schema string.

    """
    xsd_schema = etree.fromstring(xmlstring)
    json_schema = convert_to_json_schema(xsd_schema)

    return json.dumps(json_schema, sort_keys=True, indent=4, ensure_ascii=False)


def convert_to_json_schema(xml_schema):
    """Converts a LIXI XML schema to JSON schema.
    
    Args: 
        xml_schema (:obj:`lxml.etree`, required):  A lxml etree LIXI schema.
    
    Result:
        A json LIXI schema Python dict.

    """
    date_regex = "^(?:[1-9]\\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\\d|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\\d(?:0[48]|[2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)?$"
    xml_to_json_schema = {
        "string": {"type": "string"},
        "token": {"type": "string"},
        "ID": {
            "type": "string",
            "pattern": "^[a-zA-Z_][a-zA-Z0-9-_.]*$",
            "format": "lixi-ID",
        },
        "IDREF": {
            "type": "string",
            "pattern": "^[a-zA-Z_][a-zA-Z0-9-_.]*$",
            "format": "lixi-IDREF",
        },
        "base64Binary": {
            "pattern": "^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$",
            "type": "string",
        },
        "decimal": {"type": "number"},
        "integer": {"type": "integer"},
        "double": {"type": "number"},
        "dateTime": {"type": "string", "format": "lixi-datetime"},
        "date": {
            "type": "string",
            "pattern": "^(?:[1-9]\\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\\d|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\\d(?:0[48]|[2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)?$",
            "format": "lixi-date",
        },
        "gYear": {"type": "string", "format": "lixi-year"},
    }

    type_mappings = xml_to_json_schema

    def xsd_to_json_type(element_type, schema, definitions):
        """
        Where base type is found, map it to reserved types provided by default in XSD and if key is 
        being added for the first time add it to definitions as well. for now its thats not possible, 
        in worst case hardcode to string value
        
        @param element_type: a string with 
        @param schema: reference to the parent schema dict
        @param definitions: reference to the difinitions dict
        """

        # Removing the substring xs: from elements
        if "xs:" in element_type:
            element_type = element_type[3:]

        if element_type in definitions:
            schema["$ref"] = "#/definitions/" + element_type
        else:
            if element_type in type_mappings:
                definitions[element_type] = copy.deepcopy(type_mappings[element_type])

                schema["$ref"] = "#/definitions/" + element_type
            else:
                # print('The curious case of an element being referenced before put in definitions')
                schema["$ref"] = "#/definitions/" + element_type

    def add_annotation(element, schema):
        """
        Rules for parsing the xs:annotation element
    
        @param element: an xml parent element with at least one child xs:annotation
        @param schema: reference to the parent schema dict
        """

        if element.find("./xs:annotation/xs:documentation", namespaces=ns) is not None:
            schema["description"] = element.find(
                "./xs:annotation/xs:documentation", namespaces=ns
            ).text

        if (
            element.find("./xs:annotation/xs:appinfo/lx:path", namespaces=ns)
            is not None
        ):
            schema["path"] = element.find(
                "./xs:annotation/xs:appinfo/lx:path", namespaces=ns
            ).text

        if (
            element.find("./xs:annotation/xs:appinfo/lx:label", namespaces=ns)
            is not None
        ):
            schema["label"] = element.find(
                "./xs:annotation/xs:appinfo/lx:label", namespaces=ns
            ).text

        if (
            element.find("./xs:annotation/xs:appinfo/lx:references", namespaces=ns)
            is not None
        ):
            temp_array = []
            for target in element.findall(
                "./xs:annotation/xs:appinfo/lx:references/lx:target", namespaces=ns
            ):
                temp_array.append(target.text)

            schema["references"] = temp_array

        if (
            element.find(
                "./xs:annotation/xs:appinfo/lx:CustomDocumentation", namespaces=ns
            )
            is not None
        ):
            schema["custom_description"] = element.find(
                "./xs:annotation/xs:appinfo/lx:CustomDocumentation", namespaces=ns
            ).text

        if (
            element.find("./xs:annotation/xs:appinfo/lx:CustomExcerpt", namespaces=ns)
            is not None
        ):
            schema["custom_excerpt"] = element.find(
                "./xs:annotation/xs:appinfo/lx:CustomExcerpt", namespaces=ns
            ).text

    def add_attribute(element, parent_schema, passing_schema, definitions):
        """
        Rules for parsing the xs:attribute element

        @param element: an xml parent element with at least one child xs:attribute
        @param schema: reference to the parent schema dict
        @param definitions: reference to the difinitions dict
        """
        for attribute in element.findall("./xs:attribute", ns):
            temp_schema = OrderedDict()

            add_annotation(attribute, temp_schema)

            element_type = attribute.attrib["type"]
            xsd_to_json_type(element_type, temp_schema, definitions)

            if "use" in attribute.attrib:
                if attribute.attrib["use"] != "optional":
                    if "required" not in parent_schema:
                        parent_schema["required"] = []
                    parent_schema["required"].append("@" + attribute.attrib["name"])

            if "fixed" in attribute.attrib:
                temp_schema.pop("$ref", None)
                temp_schema["type"] = "string"
                temp_schema["enum"] = []
                temp_schema["enum"].append(attribute.attrib["fixed"])

            passing_schema["@" + attribute.attrib["name"]] = temp_schema

    def add_complexType(complex_type, parent_schema, passing_schema, definitions):
        """
        Rules for parsing the xs:complexType element
        
        @param complex_type: an xml element with tag xs:complexType
        @param parent_schema: reference to the parent schema of the passing schema
        @param passing_schema: reference to the parent schema of the passing schema
        @param definitions: reference to the difinitions dict
        """
        if complex_type.findall("./xs:attribute", namespaces=ns) is not None:
            add_attribute(complex_type, parent_schema, passing_schema, definitions)

    def add_simpleType(simple_type, schema, definitions):
        """
        Rules for parsing the xs:simpleType element
        
        @param simple_type: an xml element with tag xs:simpleType
        @param schema: reference to the parent schema dict
        @param definitions: reference to the difinitions dict
        """
        temp_schema = OrderedDict()

        add_annotation(simple_type, temp_schema)

        if simple_type.findall("./xs:restriction", namespaces=ns) is not None:
            add_restriction(simple_type, temp_schema, definitions)

        definitions[simple_type.attrib["name"]] = temp_schema

    def add_restriction(element, schema, definitions):
        """
        Rules for parsing restriction from an element
    
        @param element: an xml parent element with at least one child xs:restriction
        @param schema: reference to the parent schema dict
        @param definitions: reference to the difinitions dict
        """
        element_type = element.find("xs:restriction", ns).attrib["base"]
        xsd_to_json_type(element_type, schema, definitions)

        if element.find("./xs:restriction/xs:enumeration", namespaces=ns) is not None:
            add_enumeration(element, schema)

        if element.find("./xs:restriction/xs:pattern", namespaces=ns) is not None:
            add_pattern(element, schema)

        if (
            len(
                element.xpath(
                    "./xs:restriction/xs:minInclusive|./xs:restriction/xs:maxInclusive|./xs:restriction/xs:minExclusive|./xs:restriction/xs:maxExclusive",
                    namespaces=ns,
                )
            )
            > 0
        ):
            add_range(element, schema)

    def add_enumeration(element, schema):
        """
        Rules for parsing enum in an element
        
        @param element: an xml parent element with at least one child xs:enumeration
        @param schema: reference to the parent schema dict
        """
        array = []
        array_defs = {}

        for enum in element.findall("./xs:restriction/xs:enumeration", ns):

            val = enum.attrib["value"]
            array.append(val)

            temp_dict = {}

            if enum.find("./xs:annotation/xs:documentation", namespaces=ns) is not None:
                temp_dict["description"] = enum.find(
                    "./xs:annotation/xs:documentation", namespaces=ns
                ).text

            if (
                enum.find("./xs:annotation/xs:appinfo/lx:path", namespaces=ns)
                is not None
            ):
                temp_dict["path"] = enum.find(
                    "./xs:annotation/xs:appinfo/lx:path", namespaces=ns
                ).text

            if enum.find("./xs:annotation/xs:documentation", namespaces=ns) is not None:
                temp_dict["label"] = enum.find(
                    "./xs:annotation/xs:appinfo/lx:label", namespaces=ns
                ).text

            if len(temp_dict) > 0:
                array_defs[val] = temp_dict

        schema.pop("$ref", None)
        if len(array_defs) > 0:
            schema["enum_definitions"] = array_defs
        schema["enum"] = array

    def add_pattern(element, schema):
        """
        Rules for parsing Pattern in an element
        
        @param element: an xml parent element with at least one child xs:enumeration
        @param schema: reference to the parent schema dict
        """
        # TODO: XML RegEx is just being copied, IT IS NOT SIMILAR to js regex. needs conversion if poss
        schema.pop("$ref", None)
        schema["type"] = "string"
        schema["pattern"] = (
            "^" + element.find("./xs:restriction/xs:pattern", ns).attrib["value"] + "$"
        )

    def add_range(element, schema):
        """
        Rules for parsing integer range in an element
        
        @param element: an xml parent element with at least one child ./xs:restriction/xs:minInclusive|./xs:restriction/xs:maxInclusive|./xs:restriction/xs:minExclusive|./xs:restriction/xs:maxExclusive
        @param schema: reference to the parent schema dict
        """
        # TODO: XML RegEx is just being copied, IT IS NOT SIMILAR to js regex. needs conversion if poss
        schema.pop("$ref", None)

        element_type = element.find("xs:restriction", ns).attrib["base"]
        if element_type == "xs:integer":
            schema["type"] = "integer"
        else:
            schema["type"] = "number"

        if element.find("./xs:restriction/xs:minInclusive", namespaces=ns) is not None:
            schema["minimum"] = element.find(
                "./xs:restriction/xs:minInclusive", namespaces=ns
            ).attrib["value"]

        if element.find("./xs:restriction/xs:maxInclusive", namespaces=ns) is not None:
            schema["maximum"] = element.find(
                "./xs:restriction/xs:maxInclusive", namespaces=ns
            ).attrib["value"]

        if element.find("./xs:restriction/xs:minExclusive", namespaces=ns) is not None:
            schema["exclusiveMinimum"] = element.find(
                "./xs:restriction/xs:minExclusive", namespaces=ns
            ).attrib["value"]

        if element.find("./xs:restriction/xs:maxExclusive", namespaces=ns) is not None:
            schema["exclusiveMaximum"] = element.find(
                "./xs:restriction/xs:maxExclusive", namespaces=ns
            ).attrib["value"]

    def add_element(element, parent_schema, properties_schema, isComplex, definitions):
        """
        recursively parse sub elements
        
        @param element: xml.etree.ElementTree type element to step into
        @param parent_schema: dict to store sub schema values
        @param properties_schema: dict to store sub schema values
        """
        temp_schema = OrderedDict()

        element_name = element.attrib.get("name")
        min_occurs = element.attrib.get("minOccurs", "1")
        max_occurs = element.attrib.get("maxOccurs", "1")

        if max_occurs == "1":
            add_annotation(element, temp_schema)
            temp_schema_properties = OrderedDict()

            # add the required tag in the parent_schema else dont add it
            if min_occurs != "0" and not isComplex:
                if "required" not in parent_schema:
                    parent_schema["required"] = []
                parent_schema["required"].append(element_name)

            if element.attrib.get("type", "object") == "object":
                temp_schema["type"] = "object"

                if (
                    element.find("./xs:complexType", namespaces=ns) is not None
                    or isComplex is True
                ):

                    if isComplex:
                        complex_type = element
                    else:
                        complex_type = element.find("./xs:complexType", namespaces=ns)

                    add_complexType(
                        complex_type, temp_schema, temp_schema_properties, definitions
                    )

                    if (
                        complex_type.find("./xs:choice/xs:element", namespaces=ns)
                        is not None
                    ):
                        
                        if temp_schema_properties:
                            temp_schema["properties"] = {}
                            temp_schema["properties"] = copy.deepcopy(temp_schema_properties)                            
                            temp_schema["properties"]["oneOf"] = []
                        else:
                            temp_schema["oneOf"] = []

                        # create a dummy object for every elemenet so that its name can come in
                        for sub_element in complex_type.findall(
                            "./xs:choice/xs:element", namespaces=ns
                        ):
                            new_temp_dict = OrderedDict()
                            new_temp_dict["type"] = "object"
                            new_temp_dict["additionalProperties"] = False
                            new_temp_dict["properties"] = OrderedDict()

                            # handles a case where attributes come along with choice, never for elements - in this case the attr are added to ALL subsequent elements as oneOf cant have attr at same level
                            #if temp_schema_properties:
                                #new_temp_dict["properties"] = copy.deepcopy(
                                    #temp_schema_properties
                                #)

                            # Recurse
                            new_temp_dict["properties"][
                                sub_element.attrib.get("name")
                            ] = add_element(
                                sub_element,
                                new_temp_dict,
                                new_temp_dict["properties"],
                                False,
                                definitions,
                            )
                            
                            if temp_schema_properties:
                                temp_schema["properties"]["oneOf"].append(new_temp_dict)
                            else:
                                temp_schema["oneOf"].append(new_temp_dict)                            
                            
                            

                    else:
                        # cater to a single case where xml namespaces arent taken as invalid message
                        # if element_name == "Package":
                        #     temp_schema["additionalProperties"] = True
                        # else:
                        #     temp_schema["additionalProperties"] = False

                        temp_schema["additionalProperties"] = False

                        temp_schema["properties"] = temp_schema_properties

                        if (
                            complex_type.find("./xs:sequence/xs:element", namespaces=ns)
                            is not None
                        ):
                            for sub_element in complex_type.findall(
                                "./xs:sequence/xs:element", namespaces=ns
                            ):
                                # Recurse
                                temp_schema_properties[
                                    sub_element.attrib.get("name")
                                ] = add_element(
                                    sub_element,
                                    temp_schema,
                                    temp_schema_properties,
                                    False,
                                    definitions,
                                )
            else:
                # Recursion end conditions
                if element_name == "InlineAttachment" or element_name == "Comment":
                    temp_schema["type"] = "object"
                    temp_schema["additionalProperties"] = False
                    temp_schema["properties"] = OrderedDict()
                    temp_schema["properties"]["$"] = OrderedDict()
                    xsd_to_json_type(
                        element.attrib.get("type", "object"),
                        temp_schema["properties"]["$"],
                        definitions,
                    )

                else:
                    temp_schema.pop("id", None)
                    xsd_to_json_type(
                        element.attrib.get("type", "object"), temp_schema, definitions
                    )

        else:

            # as an array
            temp_array_schema = OrderedDict()

            add_annotation(element, temp_array_schema)
            temp_array_schema["type"] = "array"
            temp_array_schema["additionalItems"] = False

            temp_array_schema["items"] = OrderedDict()
            temp_array_schema["minItems"] = int(min_occurs)

            if min_occurs == "1" and not isComplex:
                if "required" not in parent_schema:
                    parent_schema["required"] = []
                parent_schema["required"].append(element_name)

            if "unbounded" not in max_occurs:
                temp_array_schema["maxItems"] = int(max_occurs)

            if element.attrib.get("type", "object") == "object":
                new_temp_dict = OrderedDict()
                new_temp_dict["type"] = "object"
                new_temp_dict["additionalProperties"] = False
                new_temp_dict["properties"] = OrderedDict()

                if element.find("./xs:complexType", namespaces=ns) is not None:
                    complex_type = element.find("./xs:complexType", namespaces=ns)
                    add_complexType(
                        complex_type,
                        new_temp_dict,
                        new_temp_dict["properties"],
                        definitions,
                    )

                    if (
                        complex_type.find("./xs:sequence/xs:element", namespaces=ns)
                        is not None
                    ):
                        for sub_element in complex_type.findall(
                            "./xs:sequence/xs:element", namespaces=ns
                        ):
                            # Recurse
                            new_temp_dict["properties"][
                                sub_element.attrib.get("name")
                            ] = add_element(
                                sub_element,
                                new_temp_dict,
                                new_temp_dict["properties"],
                                False,
                                definitions,
                            )

                temp_array_schema["items"] = new_temp_dict

            else:
                # Recursion end conditions
                if element_name == "InlineAttachment" or element_name == "Comment":
                    new_temp_dict = OrderedDict()
                    new_temp_dict["type"] = "object"
                    new_temp_dict["additionalProperties"] = False
                    new_temp_dict["properties"] = OrderedDict()
                    new_temp_dict["properties"]["$"] = OrderedDict()
                    xsd_to_json_type(
                        element.attrib.get("type", "object"),
                        new_temp_dict["properties"]["$"],
                        definitions,
                    )

                    temp_array_schema["items"] = new_temp_dict

                else:
                    new_temp_dict = OrderedDict()
                    xsd_to_json_type(
                        element.attrib.get("type", "object"), new_temp_dict, definitions
                    )
                    temp_array_schema["items"] = new_temp_dict

            # temp_schema['oneOf'].append(temp_array_schema)
            temp_schema = temp_array_schema
        return temp_schema

    # objects that will contain the converted schema
    schema = OrderedDict()
    properties = OrderedDict()
    definitions = (
        OrderedDict()
    )  # we cant make these ordered as the validator would not find compile some references before they are used.
    root = xml_schema

    # This is specified for LIXI XSD, as "Package" is an object, a more generalised approach would only contain the schema tag and definitions tag
    schema["$schema"] = "http://json-schema.org/schema#"
    schema["type"] = "object"
    schema["properties"] = properties
    schema["definitions"] = definitions
    schema["schemadetail"] = {}

    # stores description for back conversion
    schema["description"] = root.xpath(
        "./xs:annotation/xs:documentation[2]/text()", namespaces=ns
    )[0]

    # store any schema detail items
    schemadetail = root.xpath(
        "./xs:annotation/xs:appinfo/lx:schemadetail", namespaces=ns
    )[0]
    for att in schemadetail.attrib:
        schema["schemadetail"][att] = schemadetail.attrib[att]

    # store any schema detail items
    schemacustomisation = root.xpath(
        "./xs:annotation/xs:appinfo/li:schemacustomisation", namespaces=ns
    )
    if len(schemacustomisation) > 0:
        schemacustomisation = schemacustomisation[0]
        schema["schemacustomisation"] = {}

        for customization_type in schemacustomisation:
            new_array = []
            for path in customization_type:
                new_array.append(path.text)

            schema["schemacustomisation"][
                customization_type.tag.replace(
                    "{lixi.org.au/schema/appinfo_instructions}", ""
                )
            ] = new_array

    # parses and converts all xs:simpleType for definitions
    for simple_type in root.findall("./xs:simpleType", namespaces=ns):
        add_simpleType(simple_type, schema, definitions)

    # parses and converts all xs:complexType for definitions
    for complex_type in root.findall("./xs:complexType", namespaces=ns):
        definitions[complex_type.attrib.get("name")] = add_element(
            complex_type, schema, definitions, True, definitions
        )

    # recurse and add all elemenets
    for element in root.findall("./xs:element", namespaces=ns):
        properties[element.attrib.get("name")] = add_element(
            element, schema, properties, False, definitions
        )

    return schema


def convert_to_xml_schema_string(jsonstring):
    """Converts a LIXI JSON schema to XML schema.
    
    Args: 
        jsonstring (:obj:`str`, required):  A json LIXI schema string.
    
    Returns:
        A XML LIXI schema string.

    """
    json_schema = json.loads(jsonstring)
    xsd_schema = convert_to_xml_schema(json_schema)

    return etree.tostring(xsd_schema, pretty_print=True).decode("utf-8")


def convert_to_xml_schema(json_schema):
    """Converts a LIXI JSON schema to XML schema.
    
    Args: 
        json_schema (:obj:`dict`, required): A json LIXI schema dict.
    
    Returns:
        A lxml etree LIXI schema.
    """

    simpleTypesLists = []
    simpleTypesPatterns = []
    simpleTypesTypes = []
    isAnnotated = False
    isCustom = False

    def append_elements_in_order(parent, new_element):
        siblings = parent.getchildren()
        if len(siblings) == 0:
            parent.append(new_element)
        else:
            found = False
            for sibling in siblings:
                if sibling.tag == "{http://www.w3.org/2001/XMLSchema}element":
                    if (
                        sibling.attrib["name"].lower()
                        > new_element.attrib["name"].lower()
                    ):
                        parent.insert((parent.index(sibling)), new_element)
                        found = True
                        break
            if not found:
                parent.append(new_element)

    def append_attributes_in_order(parent, new_element):
        siblings = parent.getchildren()
        if len(siblings) == 0:
            parent.append(new_element)
        else:
            found = False

            for sibling in siblings:
                if sibling.tag == "{http://www.w3.org/2001/XMLSchema}attribute":
                    if (
                        sibling.attrib["name"].lower()
                        > new_element.attrib["name"].lower()
                    ):
                        parent.insert((parent.index(sibling)), new_element)
                        found = True
                        break
            if not found:
                parent.append(new_element)

    def append_simpleTypes_in_order(orderlist, new_element):

        if len(orderlist) == 0:
            orderlist.append(new_element)
        else:
            found = False

            for sibling in orderlist:
                if sibling.tag == "{http://www.w3.org/2001/XMLSchema}simpleType":
                    if (
                        sibling.attrib["name"].lower()
                        > new_element.attrib["name"].lower()
                    ):
                        orderlist.insert((orderlist.index(sibling)), new_element)
                        found = True
                        break
            if not found:
                orderlist.append(new_element)

    def ns_element(namespace, name):
        return etree.Element(etree.QName(namespace, name), nsmap=ns)

    def create_schema_annotation(parent):

        isAnnotated = False
        isCustom = False

        doc1 = ns_element(xs, "documentation")
        doc1.text = "IMPORTANT: Copyright in this schema is owned by LIXI Limited and use of the schema is controlled by the LIXI End User Licence Agreement (EULA) which can be downloaded from http://www.lixi.org.au. The EULA does not permit you to extend the schema through the addition of new elements or attributes, or modify the content model or any data values in a manner that would be inconsistent with the Standard. However you are permitted to restrict the schema such that it specifies the structures for capturing only the information you wish to receive. This statement in no way limits or modifies the terms of the EULA, and you should ensure that you are familiar with your rights and obligations under the EULA before using the schema."

        doc2 = ns_element(xs, "documentation")
        doc2.text = json_schema["description"]

        appinfo = ns_element(xs, "appinfo")

        schemadetail = ns_element(lx, "schemadetail")

        for key, item in json_schema["schemadetail"].items():

            if key == "annotation":
                if item == "Full":
                    isAnnotated = True

            if key == "type":
                if item == "Custom":
                    isCustom = True

            schemadetail.set(key, item)

        if isCustom:
            schemacustomisation = ns_element(li, "schemacustomisation")

            for key, item in json_schema["schemacustomisation"].items():

                customization_type = ns_element(li, key)
                for path in item:
                    lxpath = ns_element(li, "path")
                    lxpath.text = path
                    customization_type.append(lxpath)
                schemacustomisation.append(customization_type)

            appinfo.append(schemacustomisation)

        appinfo.append(schemadetail)
        annotation = ns_element(xs, "annotation")
        annotation.append(doc1)
        annotation.append(doc2)
        annotation.append(appinfo)

        parent.append(annotation)

        return isAnnotated, isCustom

    def create_annotation(parent, json_element):

        if isAnnotated:

            annotation = ns_element(xs, "annotation")

            documentation = ns_element(xs, "documentation")
            documentation.text = json_element["description"]

            appinfo = ns_element(xs, "appinfo")

            lx_path = ns_element(lx, "path")
            lx_path.text = json_element["path"]

            lx_label = ns_element(lx, "label")
            lx_label.text = json_element["label"]

            if isCustom:
                if "custom_description" in json_element:
                    lx_CustomDocumentation = ns_element(lx, "CustomDocumentation")
                    lx_CustomDocumentation.text = json_element["custom_description"]
                    appinfo.append(lx_CustomDocumentation)

                if "custom_excerpt" in json_element:
                    lx_CustomExcerpt = ns_element(lx, "CustomExcerpt")
                    lx_CustomExcerpt.text = json_element["custom_excerpt"]
                    appinfo.append(lx_CustomExcerpt)
            
            appinfo.append(lx_path)
            appinfo.append(lx_label)            
            
            if "references" in json_element:
                lx_references = ns_element(lx, "references")
                for target in json_element["references"]:
                    lx_target = ns_element(lx, "target")
                    lx_target.text = target
                    lx_references.append(lx_target)
                appinfo.append(lx_references)

            annotation.append(documentation)
            annotation.append(appinfo)

            parent.append(annotation)

    def create_element(parent, json_element, name=None, use=None):

        element = ns_element(xs, "element")

        # name
        if name != None:
            element.set("name", name)

        # special cases like inline attachement
        if "properties" in json_element:
            if "$" in json_element["properties"]:
                xml_type = str(json_element["properties"]["$"]["$ref"]).replace(
                    "#/definitions/", ""
                )
                element.set("type", xml_type)

        # Type
        xml_type = None
        if "type" in json_element:
            if json_element["type"] == "object":
                json_type = json_element["type"]

                if json_type == "base64Binary":
                    xml_type = "base64BinaryType"
                elif json_type == "base64Binary":
                    xml_type = "currencyType"
                elif json_type == "dateTime":
                    xml_type = "dateTimeType"
                elif json_type == "date":
                    xml_type = "dateType"
                elif json_type == "decimal":
                    xml_type = "decimalType"
                elif json_type == "gYear":
                    xml_type = "gYearType"
                elif json_type == "integer":
                    xml_type = "integerType"
                elif json_type == "ID":
                    xml_type = "percentType"
                elif json_type == "IDREF":
                    xml_type = "referenceType"
                elif json_type == "string":
                    xml_type = "stringType"
                elif json_type == "ID":
                    xml_type = "uniqueIDType"
            elif json_element["type"] == "array":
                if "$ref" in json_element["items"]:
                    xml_type = str(json_element["items"]["$ref"]).replace(
                        "#/definitions/", ""
                    )

        elif "$ref" in json_element:
            xml_type = str(json_element["$ref"]).replace("#/definitions/", "")

        if xml_type != None:
            element.set("type", xml_type)

        if parent.tag != "{http://www.w3.org/2001/XMLSchema}schema":
            # Type
            min_occurs = "0"  # default LIXI preference
            max_occurs = "1"

            if use == "required":
                min_occurs = "1"

            if "type" in json_element:
                if json_element["type"] == "array":

                    min_occurs = "0"
                    max_occurs = "unbounded"

                    if "minItems" in json_element:
                        min_occurs = str(json_element["minItems"])

                    if "maxItems" in json_element:
                        max_occurs = str(json_element["maxItems"])

            element.set("minOccurs", min_occurs)
            element.set("maxOccurs", max_occurs)

        create_annotation(element, json_element)

        create_complexType(element, json_element, name=None)

        append_elements_in_order(parent, element)

    def create_attribute(parent, json_element, name=None, use=None):
        attribute = ns_element(xs, "attribute")

        # name
        attribute.set("name", name[1:])

        # Type
        xml_type = None
        if "type" in json_element:
            xml_type = "stringType"
            json_type = json_element["type"]

            if json_type == "base64Binary":
                xml_type = "base64BinaryType"
            elif json_type == "dateTime":
                xml_type = "dateTimeType"
            elif json_type == "date":
                xml_type = "dateType"
            elif json_type == "decimal":
                xml_type = "decimalType"
            elif json_type == "gYear":
                xml_type = "gYearType"
            elif json_type == "integer":
                xml_type = "integerType"
            elif json_type == "IDREF":
                xml_type = "referenceType"
            elif json_type == "string":
                xml_type = "stringType"
            elif json_type == "ID":
                xml_type = "uniqueIDType"

        elif "$ref" in json_element:
            xml_type = str(json_element["$ref"]).replace("#/definitions/", "")

        if xml_type != None:
            attribute.set("type", xml_type)

        # use
        attribute.set("use", use)

        # fixed
        if xml_type == "stringType" and "enum" in json_element:
            if len(json_element["enum"]) == 1:
                attribute.set("fixed", json_element["enum"][0])

        # annotation
        create_annotation(attribute, json_element)

        append_attributes_in_order(parent, attribute)

    def create_complexType(parent, json_element, name=None):

        complexType = ns_element(xs, "complexType")

        if name != None:
            complexType.set("name", name)
            create_annotation(complexType, json_element)

        if "properties" in json_element:  ##type is object

            ##run loop twice to account for sequence
            sequence = ns_element(xs, "sequence")
            for key, item in json_element["properties"].items():
                if key[:1] != "@" and key != "$" and key != "oneOf":
                    if "required" in json_element:
                        use = (
                            "required"
                            if key in json_element["required"]
                            else "optional"
                        )
                    else:
                        use = "optional"

                    create_element(sequence, item, key, use)

            if len(sequence.getchildren()) > 0:
                complexType.append(sequence)
            
                
            for key, item in json_element["properties"].items():
                
                    
                if key == "oneOf":
                    
                    choice = ns_element(xs, "choice")
        
                    for choice_item in json_element["properties"]["oneOf"]:
                        for key, item in choice_item["properties"].items():
                            if key[:1] != "@":
                                if "required" in choice_item:
                                    use = (
                                        "required"
                                        if key in choice_item["required"]
                                        else "optional"
                                    )
                                else:
                                    use = "optional"
        
                                create_element(choice, item, key, use)
        
                    complexType.append(choice)
                    
            for key, item in json_element["properties"].items():       
                
                if key[:1] == "@":

                    if "required" in json_element:
                        use = (
                            "required"
                            if key in json_element["required"]
                            else "optional"
                        )
                    else:
                        use = "optional"

                    create_attribute(complexType, item, key, use)                    
                    

        elif "items" in json_element:  ##type is array:

            ##run loop twice to account for sequence
            sequence = ns_element(xs, "sequence")
            if "properties" in json_element["items"]:
                for key, item in json_element["items"]["properties"].items():
                    if key[:1] != "@" and key != "$":
                        if "required" in json_element:
                            use = (
                                "required"
                                if key in json_element["required"]
                                else "optional"
                            )
                        else:
                            use = "optional"

                        create_element(sequence, item, key, use)

            if len(sequence.getchildren()) > 0:
                complexType.append(sequence)

            if "properties" in json_element["items"]:
                for key, item in json_element["items"]["properties"].items():
                    if key[:1] == "@":
                        if "required" in json_element["items"]:
                            use = (
                                "required"
                                if key in json_element["items"]["required"]
                                else "optional"
                            )
                        else:
                            use = "optional"

                        create_attribute(complexType, item, key, use)

        elif "oneOf" in json_element:  ##type is choice/oneof:

            choice = ns_element(xs, "choice")

            for choice_item in json_element["oneOf"]:

                for key, item in choice_item["properties"].items():
                    if key[:1] != "@":
                        if "required" in choice_item:
                            use = (
                                "required"
                                if key in choice_item["required"]
                                else "optional"
                            )
                        else:
                            use = "optional"

                        create_element(choice, item, key, use)

            complexType.append(choice)

            first_choice_item = json_element["oneOf"][
                0
            ]  ##if there are attributes for choice they added to all oneOf items in json hence grabbing attributes from the first only will suffice

            for key, item in first_choice_item["properties"].items():
                if key[:1] == "@":
                    if "required" in json_element:
                        use = (
                            "required"
                            if key in json_element["required"]
                            else "optional"
                        )
                    else:
                        use = "optional"

                    create_attribute(complexType, item, key, use)

        if len(complexType.getchildren()) > 0:
            parent.append(complexType)

    def create_enumeration(parent, json_element, name=None):

        enumeration = ns_element(xs, "enumeration")

        enumeration.set("value", name)
        if isAnnotated:
            create_annotation(enumeration, json_element["enum_definitions"][name])

        parent.append(enumeration)

    def create_simpleType(parent, json_element, name=None):
        simpleType = ns_element(xs, "simpleType")

        if name != None:
            simpleType.set("name", name)
            create_annotation(simpleType, json_element)

        restriction = ns_element(xs, "restriction")

        if "enum" in json_element:  ##simpletype is a List
            restriction.set("base", "xs:token")

            for enum in json_element["enum"]:
                create_enumeration(restriction, json_element, enum)

            simpleType.append(restriction)
            append_simpleTypes_in_order(simpleTypesLists, simpleType)

        elif "pattern" in json_element:  ##simpletype is Pattern

            patt = str(json_element["pattern"]).replace("\\\\", "\\")[1:-1]

            restriction.set("base", "xs:string")
            pattern = ns_element(xs, "pattern")
            pattern.set("value", patt)
            restriction.append(pattern)
            simpleType.append(restriction)
            append_simpleTypes_in_order(simpleTypesPatterns, simpleType)

        elif "$ref" in json_element:  ##simpletype is a Type

            if name == "base64BinaryType":
                restriction.set("base", "xs:base64Binary")
            elif name == "currencyType":
                restriction.set("base", "xs:decimal")
            elif name == "dateTimeType":
                restriction.set("base", "xs:dateTime")
            elif name == "dateType":
                restriction.set("base", "xs:date")
            elif name == "decimalType":
                restriction.set("base", "xs:decimal")
            elif name == "gYearType":
                restriction.set("base", "xs:gYear")
            elif name == "integerType":
                restriction.set("base", "xs:integer")
            elif name == "percentType":
                restriction.set("base", "xs:decimal")
            elif name == "referenceType":
                restriction.set("base", "xs:IDREF")
            elif name == "stringType":
                restriction.set("base", "xs:string")
            elif name == "uniqueIDType":
                restriction.set("base", "xs:ID")

            simpleType.append(restriction)
            append_simpleTypes_in_order(simpleTypesTypes, simpleType)

        elif (
            "minimum" in json_element or "maximum" in json_element
        ):  ##simpletype is a Range

            if json_element["type"] == "decimal":
                restriction.set("base", "xs:decimal")
            elif json_element["type"] == "integer":
                restriction.set("base", "xs:integer")
            elif json_element["type"] == "string":
                if "format" in json_element:
                    if json_element["format"] == "lixi-year":
                        restriction.set("base", "xs:gYear")
                    elif json_element["format"] == "lixi-datetime":
                        restriction.set("base", "xs:dateTime")
                    elif json_element["format"] == "lixi-date":
                        restriction.set("base", "xs:date")
                else:
                    restriction.set("base", "xs:string")

            if "minimum" in json_element:
                minInclusive = ns_element(xs, "minInclusive")
                minInclusive.set("value", json_element["minimum"])
                restriction.append(minInclusive)

            if "maximum" in json_element:
                maxInclusive = ns_element(xs, "maxInclusive")
                maxInclusive.set("value", json_element["maximum"])
                restriction.append(maxInclusive)

            simpleType.append(restriction)
            append_simpleTypes_in_order(simpleTypesTypes, simpleType)

    json_schema = json.loads(json_schema)
    isAnnotated = False

    Schema = ns_element(xs, "schema")
    Schema.set("elementFormDefault", "qualified")
    Schema.set("attributeFormDefault", "unqualified")
    Schema.set("version", "1.0")
    isAnnotated, isCustom = create_schema_annotation(Schema)

    # Package
    create_element(Schema, json_schema["properties"]["Package"], "Package", "required")

    # cater to all complex types and simple types
    for key, item in json_schema["definitions"].items():
        if "type" in item:
            if item["type"] == "object":
                create_complexType(Schema, item, key)
            elif key.endswith("Pattern"):
                create_simpleType(Schema, item, key)
            elif key.endswith("Range"):
                create_simpleType(Schema, item, key)
        else:
            if key.endswith("Type"):
                create_simpleType(Schema, item, key)
            elif key.endswith("List"):
                create_simpleType(Schema, item, key)

    # Sort the xml schema as per lixi order.
    simpleTypeList = simpleTypesLists + simpleTypesPatterns + simpleTypesTypes
    for simpletype in simpleTypeList:
        Schema.append(simpletype)

    return Schema


### Output code
# with io.open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_19-Annotated.xsd','r', encoding="utf-8") as xml_file:
# xml_schema = xml_file.read()
# parser = etree.XMLParser(remove_blank_text=True)
# xsd_schema = etree.fromstring(xml_schema, parser)
# json_schema = convert_to_json_schema(xsd_schema)
# with io.open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_19_RFC-Annotated-CREATED.json',"wb+") as f:
# string = json.dumps(json_schema, sort_keys=True, indent=4, ensure_ascii=False).encode('utf-8')
# f.write(string)
###
# with io.open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_19_RFC-Annotated-CREATED.json','r', encoding="utf-8") as json_file:
# json_schema = json_file.read()
# xml_schema = convert_to_xml_schema(json_schema)
# with io.open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_19-Annotated-CREATED.xsd',"wb+") as f:
# string = etree.tostring(xml_schema, pretty_print=True, encoding='UTF-8')
# f.write(string)


##Code for better diff comparison
# xsd_schema = etree.parse('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_21-Annotated.xsd')
# json_schema = convert_to_json_schema(xsd_schema.getroot())
# with open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_21-Annotated-CREATED.json',"w+") as f:
# f.write(json.dumps(json_schema, sort_keys=True, indent=4))


# with open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_21-Annotated-CREATED.json','r') as json_file:
# json_schema = json_file.read()
# xml_schema = convert_to_xml_schema(json_schema)
# with open('C:/Users/compb/Downloads/xml/LIXI-CAL-2_6_21-Annotated-CREATED.xsd',"w+") as f:
# f.write(etree.tostring(xml_schema, pretty_print=True).decode('utf-8'))

# print("Done")
