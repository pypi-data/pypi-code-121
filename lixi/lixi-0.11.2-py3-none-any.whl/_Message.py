import json as _json
from lxml import etree as _etree
import re, io, os

ns = {
    "xs": "http://www.w3.org/2001/XMLSchema",
    "lx": "lixi.org.au/schema/appinfo_elements",
    "li": "lixi.org.au/schema/appinfo_instructions",
}

if __name__ == "__main__":
    import _xml_to_json, _path_functions, _jsonschema_functions, _xslt_transform, _schematron_functions
    from _LIXI import (
        LIXI as _LIXI,
        LIXIValidationError,
        LIXIInvalidSyntax,
        LIXIResouceNotFoundError,
    )
else:
    from lixi import (
        _xml_to_json,
        _path_functions,
        _jsonschema_functions,
        _xslt_transform,
        _schematron_functions,
    )
    from lixi._LIXI import (
        LIXI as _LIXI,
        LIXIValidationError,
        LIXIInvalidSyntax,
        LIXIResouceNotFoundError,
    )


class Message:
    """A LIXI message object (either XML or JSON) that conforms to a LIXI2 standard.
        
    The class exists as a wrapper for all internal message functions the library is to provide.
    """

    def __init__(self, data, message_path, file_type):
        """Creates a LIXI message XML.
    
        Args:
            data (:obj:`str`, optional): A LIXI Message provided as a string. Defaults to None.
            message_path (:obj:`str`, optional) : A LIXI Message provided as a path. Defaults to None.
            file_type (:obj:`str`, optional): The type of the input LIXI Message given. Defaults to 'xml'. DEPRECATED. But have kept it for later use if needed.
    
        Returns:
            A LIXI message instance.
    
        Raises:
            LIXIResouceNotFoundError: If the schema is not found at the schema path.
            LIXIInvalidSyntax: If the schema file is not well formed.
        """

        self.xml_package = None
        self.json_package = None

        self.json_string = None
        self.file_type = None

        self.schema_name = None
        self.is_valid = None
        self.validation_message = None

        # If data specified as source
        if data != None and message_path == None:
            # just a check to ensure 
            data = re.sub(r'\<\?.*?\?\>', '', data)
            
            passed = False
            if passed == False:
                try:
                    parser = _etree.XMLParser(remove_blank_text=True)
                    self.xml_package = _etree.fromstring(data, parser)
                    passed = True
                    self.file_type = "xml"
                except Exception as e:
                    passed = False

            if passed == False:
                try:
                    self.json_string = str(data)
                    self.json_package = _json.loads(data)

                    passed = True
                    self.file_type = "json"
                except Exception as e:
                    passed = False

        # If path specified as source
        elif data == None and message_path != None:
            passed = False
            
            if os.path.exists(message_path) == False:
                raise LIXIResouceNotFoundError(message_path)
            
            if passed == False:
                try:
                    self.xml_package = _etree.parse(message_path)
                    self.xml_package = self.xml_package.getroot()
                    passed = True
                    self.file_type = "xml"
                except Exception as e:
                    passed = False

            if passed == False:
                try:

                    with io.open(message_path, "r", encoding="utf-8") as json_file:
                        self.json_string = str(json_file.read())
                        self.json_package = _json.loads(str(self.json_string))

                    passed = True
                    self.file_type = "json"
                except Exception as e:
                    passed = False

        # Checking for some required fields
        if self.file_type == "xml":

            self.is_json = False

            try:
                self.lixi_transaction_type = self.xml_package.xpath(
                    "/Package/SchemaVersion/@LIXITransactionType"
                )[0]
            except IndexError:
                raise LIXIInvalidSyntax(
                    "Message read failed. XML Message does not have the attribute 'Package.SchemaVersion.LIXITransactionType' populated."
                )

            try:
                self.lixi_version = self.xml_package.xpath(
                    "/Package/SchemaVersion/@LIXIVersion"
                )[0]
            except IndexError:
                raise LIXIInvalidSyntax(
                    "Message read failed. XML Message does not have the attribute 'Package.SchemaVersion.LIXIVersion' populated."
                )

            try:
                self.lixi_custom_version = self.xml_package.xpath(
                    "/Package/SchemaVersion/@LIXICustomVersion"
                )[0]
            except IndexError:
                self.lixi_custom_version = None
            
            try:
                self.publisher_lixicode = self.xml_package.xpath(
                    "/Package/Publisher/@LIXICode"
                )[0]
            except IndexError:
                self.publisher_lixicode = None
                
            try:
                self.broker_reference = self.xml_package.xpath(
                    "/Package/Content/Application/Overview/@BrokerApplicationReferenceNumber"
                )[0]
            except IndexError:
                self.broker_reference = None
                
            try:
                self.lender_reference = self.xml_package.xpath(
                    "/Package/Content/Application/Overview/@LenderApplicationReferenceNumber"
                )[0]
            except IndexError:
                self.lender_reference = None
                    
            try:
                self.lodgement_reference = self.xml_package.xpath(
                    "/Package/Content/Application/Overview/@LodgementReferenceNumber"
                )[0]
            except IndexError:
                self.lodgement_reference = None
                
            try:
                self.valuation_requestor_assigned_id = self.xml_package.xpath(
                    "/Package/Content/RealEstateValuation/ValuationOrder/@RequestorAssignedID"
                )[0]
            except IndexError:
                self.valuation_requestor_assigned_id = None
                
            try:
                self.valuation_valuer_assigned_id = self.xml_package.xpath(
                    "/Package/Content/RealEstateValuation/@ValuerAssignedID"
                )[0]
            except IndexError:
                self.valuation_valuer_assigned_id = None
                
            try:
                self.valuation_avm_assigned_id = self.xml_package.xpath(
                    "/Package/Content/RealEstateValuation/@AVMReferenceID"
                )[0]
            except IndexError:
                self.valuation_avm_assigned_id = None                        

        elif self.file_type == "json":

            self.is_json = True

            try:
                self.lixi_transaction_type = str(
                    self.json_package["Package"]["SchemaVersion"][
                        "@LIXITransactionType"
                    ]
                )
            except Exception:
                raise LIXIInvalidSyntax(
                    "Message read failed. JSON Message does not have the attribute 'Package.SchemaVersion.LIXITransactionType' populated."
                )

            try:
                self.lixi_version = str(
                    self.json_package["Package"]["SchemaVersion"]["@LIXIVersion"]
                )
            except Exception:
                raise LIXIInvalidSyntax(
                    "Message read failed. JSON Message does not have the attribute 'Package.SchemaVersion.LIXIVersion' populated."
                )

            try:
                self.lixi_custom_version = str(
                    self.json_package["Package"]["SchemaVersion"]["@LIXICustomVersion"]
                )
            except Exception:
                self.lixi_custom_version = None
                
            try:
                self.publisher_lixicode = str(
                    self.json_package["Package"]["Publisher"]["@LIXICode"]
                )
            except Exception:
                self.publisher_lixicode = None
                
            try:
                self.broker_reference = str(
                    self.json_package["Package"]["Content"]["Application"]["Overview"]["@BrokerApplicationReferenceNumber"]
                )
            except Exception:
                self.broker_reference = None 
                
            try:
                self.lender_reference = str(
                    self.json_package["Package"]["Content"]["Application"]["Overview"]["@LenderApplicationReferenceNumbe"]
                )
            except Exception:
                self.lender_reference = None 
                
            try:
                self.lodgement_reference = str(
                    self.json_package["Package"]["Content"]["Application"]["Overview"]["@LodgementReferenceNumber"]
                )
            except Exception:
                self.lodgement_reference = None                            
            
            try:
                self.valuation_requestor_assigned_id = str(
                    self.json_package["Package"]["Content"]["RealEstateValuation"]["ValuationOrder"]["@RequestorAssignedID"]
                )
            except Exception:
                self.valuation_requestor_assigned_id = None 
                
            try:
                self.valuation_valuer_assigned_id = str(
                    self.json_package["Package"]["Content"]["RealEstateValuation"]["@ValuerAssignedID"]
                )
            except Exception:
                self.valuation_valuer_assigned_id = None 
                
            try:
                self.valuation_avm_assigned_id = str(
                    self.json_package["Package"]["Content"]["RealEstateValuation"]["@AVMReferenceID"]
                )
            except Exception:
                self.valuation_avm_assigned_id = None              
            
        else:  # everything failed now we need better error messages
            ##Better error messages
            error_message = ""

            if data == None and message_path != None:
                with io.open(message_path, "r", encoding="utf-8") as file:
                    data = str(file.read())

            if '"Package"' in data:  ## is json
                try:
                    _json.loads(str(data))
                except Exception as e:
                    error_message = e
            elif "<Package>" in data:
                try:
                    parser = _etree.XMLParser(remove_blank_text=True)
                    doc = _etree.fromstring(data, parser)
                except Exception as e:
                    error_message = e

            raise LIXIInvalidSyntax(
                "Message read failed. Message can not be read or type is not supported.\n"
                + str(error_message)
            )

    def __write__(self, default_name, output_path, data, error_string):
        """Helper function to write to a file.

        Args:
            default_name (:obj:`str`, required): A default name in case the provided out path is a folder path and not a complete file path.
            output_path (:obj:`str`, required): The output path of the file to be written.
            data (:obj:`str`, required): Data to be written to the  file.
            error_string (:obj:`str`, required): A context specific error string in case write fails.

        Raises:
            LIXIResouceNotFoundError: If output path provided does not exist.
        """

        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, default_name)

        try:
            with io.open(output_path, "w+", encoding="utf-8") as out_file:
                out_file.write(data)
        except Exception as e:
            raise LIXIResouceNotFoundError(error_string)

    def to_json(self, return_instance=False):
        """Converts the LIXI XML Message object to a LIXI JSON Message object. Alternatively, returns a LIXI JSON Message object if return_instance parameter is set to True. 

        Args:
            return_instance (:obj:`bool`, required): Indicates if a LIXI message instance needs to be created from the result and returned. 

        Returns:
            Equivalent LIXI JSON message instance ONLY if return_instance is set to True. 

        Raises:
            LIXIInvalidSyntax: Message file is corrupted.
        """

        # for converstion an xsd is required to properly arrange elements.
        schema_etree = _LIXI.getInstance().fetch_xml_schema(
            lixi_transaction_type=self.lixi_transaction_type,
            lixi_version=self.lixi_version,
            custom_version=self.lixi_custom_version,
            return_annotated = True
        )
        schema_etree = _etree.fromstring(schema_etree)        

        if self.json_package == None:
            self.json_package = _xml_to_json.to_json(self.xml_package, schema_etree)

        if return_instance == True:
            return Message(
                _json.dumps(
                    self.json_package, sort_keys=True, indent=4, ensure_ascii=False
                ),
                None,
                "json",
            )
        else:
            self.file_type = "json"
            self.is_json = True

    def to_xml(self, return_instance=False):
        """Converts a LIXI JSON Message object to a LIXI XML Message object. Alternatively, returns a LIXI XML Message object if return_instance parameter is set to True. 


        Args:
            return_instance (:obj:`bool`, required): Indicates if a LIXI message instance needs to be created from the result and returned. 

        Returns:
            Equivalent LIXI XML message instance ONLY if return_instance is set to True. 

        Raises:
            LIXIInvalidSyntax: Message file is corrupted.
        """

        # for converstion an xsd is required hence setting it to be false
        schema_etree = _LIXI.getInstance().fetch_xml_schema(
            lixi_transaction_type=self.lixi_transaction_type,
            lixi_version=self.lixi_version,
            custom_version=self.lixi_custom_version,
            return_annotated = True
        )
        schema_etree = _etree.fromstring(schema_etree)

        if self.xml_package == None:
            self.xml_package = _xml_to_json.to_xml(self.json_package, schema_etree)

        if return_instance == True:
            return Message(
                _etree.tostring(self.xml_package, pretty_print=True).decode("utf-8"),
                None,
                "xml",
            )
        else:
            self.file_type = "xml"
            self.is_json = False

    def get_message_paths(self, output_path=None):
        """Derives all LIXI Paths (the full path of elements and attributes separated by dots, eg Package.Content.Application) within this LIXI Message object.

        Args:
            output_path (:obj:`str`, optional): Path to write the message paths list to. Defaults to None.

        Returns:
            A list of element paths in the Message. 

        Raises:
            LIXIResouceNotFoundError: If the output path provided is not correct.
        """

        # Schema to be used as per message to derive paths from
        schema = _LIXI.getInstance().fetch_xml_schema(
            lixi_transaction_type=self.lixi_transaction_type,
            lixi_version=self.lixi_version,
            custom_version=self.lixi_custom_version,
            return_annotated = True            
        )
        schema = _etree.fromstring(schema)

        # Incase this is a json message, functionality works with xml only
        if self.xml_package == None:
            self.xml_package = _xml_to_json.to_xml(self.json_package, schema)

        message_paths_list = _path_functions.get_paths_for_elements(
            message=self, schema=schema
        )

        # output to a path
        if output_path == None:
            return message_paths_list
        else:
            self.__write__(
                "message_paths_output.txt",
                output_path,
                ",\n".join(message_paths_list),
                "Message get paths failed. Can not store the schema at the specified folder.",
            )
            return message_paths_list

    def get_schema_paths(self, exploded=False, output_path=None):
        """Gets all the elements paths of the LIXI schema associated with this LIXI Message instance.
        Derives all LIXI Paths (the full path of elements and attributes separated by dots, eg Package.Content.Application) available in the schema corresponding to the this LIXI Message object.

        Args:
            exploded (:obj:`bool`, optional): Variable to indicate if the returned schema should be exploded or not. 
            output_path (:obj:`str`, optional): Path to write the schema paths list to. Defaults to None.

        Returns:
            A list of element paths in the LIXI schema. 

        Raises:
            LIXIResouceNotFoundError: If the output path provided is not correct.
        """

        # Gets the schema paths from LIXI function
        schema_paths_list = _LIXI.getInstance().get_schema_paths(
            self.lixi_transaction_type,
            self.lixi_version,
            "xml",
            self.lixi_custom_version,
            None,
            None,
            exploded
        )

        # Output paths
        if output_path == None:
            return schema_paths_list
        else:
            self.__write__(
                "schema_paths_output.txt",
                output_path,
                ",".join(schema_paths_list),
                "Message get schema paths failed. Can not store the schema at the specified folder.",
            )
            return schema_paths_list

    def get_restriction_paths_for_schema(self, output_path=None):
        """Gets the customization instructions file which can be used for a generating a customised schema based on the subset of elements and attributes that are actually included in this LIXI Message object.

        Args:
            output_path (:obj:`str`, optional): Path to write the schema paths list to. Defaults to None.

        Returns:
            A string of blacklist customization restrictions xml that can be utilized by this library to generate a custom schema. 

        Raises:
            LIXIResouceNotFoundError: If the output path provided is not correct.
        """

        message_paths = self.get_message_paths()
        schema_paths = self.get_schema_paths()

        customization_instructions = _path_functions.get_blacklist_paths_for_customization(
            self.lixi_transaction_type, message_paths, schema_paths
        )

        if output_path == None:
            return customization_instructions
        else:
            self.__write__(
                "customization_instructions_output.xml",
                output_path,
                customization_instructions,
                "Message get restriction paths failed. Can not store the schema at the specified folder.",
            )
            return customization_instructions

    def get_custom_schema(self, output_path=None):
        """Generates a schema using Customisation by Restriction based on the subset of elements and attributes that are actually included in this LIXI Message object.
    
        Args:
            output_path (:obj:`str`, optional): Path to write the schema paths list to. Defaults to None.
    
        Returns:
            A customised LIXI schema as a string which can also be to the output folder specified. 
    
        Raises:
            LIXIInvalidSyntax: Validation errors for the lixi version or transaction type.
            LIXIResouceNotFoundError: If path provided does not exist.
            LIXIValidationError: validation error in the customization instructions.
        """

        # Read the instructions file
        restriction_paths = self.get_restriction_paths_for_schema(output_path=None)

        # Generate the customised schema as string
        if output_path == None:
            return _LIXI.getInstance().generate_custom_schema(
                instructions=restriction_paths,
                lixi_transaction_type=self.lixi_transaction_type,
                lixi_version=self.lixi_version,
                output_name=None,
                output_folder=None,
                output_type=self.file_type,
            )
        else:

            basename = os.path.basename(output_path)
            dirname = os.path.dirname(output_path)

            if os.path.isdir(output_path):
                output_folder = output_path
                output_name = None
            elif os.path.isfile(output_path):
                output_folder = dirname
                output_name = (
                    str(basename)
                    .replace(".xsd", "")
                    .replace(".json", "")
                    .replace(".txt", "")
                )
            elif (
                ".json" in basename
                or ".xsd" in basename
                or ".xml" in basename
                or ".txt" in basename
            ):
                output_folder = dirname
                output_name = (
                    str(basename)
                    .replace(".xsd", "")
                    .replace(".json", "")
                    .replace(".txt", "")
                )
            else:
                output_folder = None
                output_name = None

            return _LIXI.getInstance().generate_custom_schema(
                instructions=restriction_paths,
                lixi_transaction_type=self.lixi_transaction_type,
                lixi_version=self.lixi_version,
                output_name=output_name,
                output_folder=output_folder,
                output_type=self.file_type,
            )

    def transform_message(self, xslt_folder_path, to_version=None, return_instance=False):
        """Transforms a LIXI Message instance to an older/newer version, based on the schema version specified, of the LIXI Message instance.
    
        Args:
            xslt_folder_path (:obj:`bool`, required): A path to a folder containing LIXI transformation (.xslt) files. 
            to_version (:obj:`str`, optional): The version of the LIXI schema to be transformed to. Should be in the format of '2.6.24'. Defaults to the latest version if not provided.
            return_instance (:obj:`bool`, optional): Indicates if a LIXI message instance needs to be created from the result and returned. 
    
        Returns:
            Transformed LIXI Message instance ONLY if return_instance is set to True.
    
        Raises:
            LIXIResouceNotFoundError: If the schema is not found at the schema path.
            LIXIInvalidSyntax: If the schema file is not well formed.
        """
        
        # Incase this is a json message, functionality works with xml only
        if self.xml_package == None:
            
            # Schema to be used as per message to derive paths from
            schema = _LIXI.getInstance().fetch_xml_schema(
                lixi_transaction_type=self.lixi_transaction_type,
                lixi_version=self.lixi_version,
                custom_version=self.lixi_custom_version,
                return_annotated = False 
            )
            schema = _etree.fromstring(schema)            
            
            self.xml_package = _xml_to_json.to_xml(self.json_package, schema)

        from_version_str = self.lixi_version
        transaction_type = self.lixi_transaction_type

        if to_version == None:
            
            if _LIXI.getInstance().schema_folder_path == None:
                raise LIXIResouceNotFoundError(
                    "Please specify the transformation version or please set the schema folder with lixi.set_schema_folder() .\n"
                    + str(error_message)
                )            
            
            to_version_str = str(
                _LIXI.getInstance().get_schema_latest_version(transaction_type)
            ).replace("_", ".")
        else:
            to_version_str = to_version

        result, all_warnings = _xslt_transform.transform_xslt(
            self.xml_package, xslt_folder_path, transaction_type, from_version_str, to_version_str
        )

        if return_instance == True:
            return Message(
                _etree.tostring(result, pretty_print=True).decode("utf-8"), None, "xml",
            )
        else:
            self.xml_package = result

    def get_transform_warnings(self, xslt_folder_path, to_version=None, output_path=None):
        """Gets the warnings when transforming a LIXI Message instance. Contains a record of data lost in the Message.
    
        Args:
            xslt_folder_path (:obj:`bool`, required): A path to a folder containing LIXI transformation (.xslt) files. 
            to_version (:obj:`str`, required): The version of the LIXI schema to be transformed to. Should be in the format of '2.6.24'. Defaults to the latest version if not provided.
            output_path (:obj:`str`, optional): Path to write the schema paths list to. Defaults to None.
    
        Returns:
            A string of xsl transform warnings.
    
        Raises:
            LIXIResouceNotFoundError: If the schema is not found at the schema path.
            LIXIInvalidSyntax: If the schema file is not well formed.
        """

        # Incase this is a json message, functionality works with xml only
        if self.xml_package == None:
            # Schema to be used as per message to derive paths from
            schema = _LIXI.getInstance().fetch_xml_schema(
                lixi_transaction_type=self.lixi_transaction_type,
                lixi_version=self.lixi_version,
                custom_version=self.lixi_custom_version,
                return_annotated = False
            )
            schema = _etree.fromstring(schema)            
            
            self.xml_package = _xml_to_json.to_xml(self.json_package, schema)

        from_version_str = self.lixi_version
        transaction_type = self.lixi_transaction_type

        if to_version == None:
            if _LIXI.getInstance().schema_folder_path == None:
                raise LIXIResouceNotFoundError(
                    "Please specify the transformation version or please set the schema folder with lixi.set_schema_folder() .\n"
                    + str(error_message)
                )            
            
            to_version_str = str(
                _LIXI.getInstance().get_schema_latest_version(transaction_type)
            ).replace("_", ".")
        else:
            to_version_str = to_version

        result, all_warnings = _xslt_transform.transform_xslt(
            self.xml_package, xslt_folder_path, transaction_type, from_version_str, to_version_str
        )

        if output_path == None:
            return all_warnings
        else:
            self.__write__(
                "transform_warnings_output.xml",
                output_path,
                all_warnings,
                "Message transform warnings failed. Can not store the schema at the specified folder.",
            )
            return all_warnings

    def validate_schematron(
        self, schematron_schema_text=None, schematron_schema_path=None
    ):
        """Validates this LIXI Message object against a Schematron file containing rules and assertions.
    
        Args:
            schematron_schema_text (:obj:`str`, required): Schematron rules schema provided as a text.
            schematron_schema_path (:obj:`str`, required): Schematron rules schema provided as a path.
    
        Result:
            result (:obj:`bool`): Indicates if validation was successfull.
            message (:obj:`str`): Validation message.
            error_log (:obj:`list`): Validation error object as a Python List.
    
        Raises:
            LIXIResouceNotFoundError: If the schema is not found at the schema path.
            LIXIInvalidSyntax: If the schema file is not well formed.
        """

        # Incase this is a json message, functionality works with xml only
        if self.xml_package == None:
            # Schema to be used as per message to derive paths from
            schema = _LIXI.getInstance().fetch_xml_schema(
                lixi_transaction_type=self.lixi_transaction_type,
                lixi_version=self.lixi_version,
                custom_version=self.lixi_custom_version,
                return_annotated = False
            )
            schema = _etree.fromstring(schema)            
            
            self.xml_package = _xml_to_json.to_xml(self.json_package, schema)

        if schematron_schema_path != None:
            if os.path.exists(schematron_schema_path) == True:
                f = io.open(schematron_schema_path, mode="r", encoding="utf-8")
                schematron_schema_text = f.read()
                f.close()
            else:
                raise LIXIResouceNotFoundError(
                    "Message schematron validation failed. Schematron rules schema file not found at the specified path."
                )

        try:
            parser = _etree.XMLParser(remove_blank_text=True)
            schematron_schema_etree = _etree.fromstring(schematron_schema_text, parser)
        except Exception as e:
            raise LIXIInvalidSyntax(
                "Message schematron validation failed. The schematron schema is not well-formed.\n\nError Message:\n    "
                + str(e)
            )

        result, message, error_log = _schematron_functions.validate(
            self.xml_package, schematron_schema_etree
        )

        return result, message, error_log

    def validate(self, schema=None, schema_path=None):
        """Validates this LIXI Message object against the corresponding LIXI schema.

        Args:
            schema (:obj:`str`, required): LIXI schema provided as a string. Defaults to None.  
            schema_path (:obj:`str`, required): LIXI schema provided as a path. Defaults to None.

        Result:
            result (:obj:`bool`): Indicates if validation was successfull.
            message (:obj:`str`): Validation message.
            error_log (:obj:`list`): Validation errors in list.

        Raises:
            LIXIValidationError: Validation errors for the xml file.
        """
        
        class Error_Log:
            """Represents a Error when validating with a schematron file.
                
            """
            def __init__(self, message, test, message_line, message_location):
                """Creates a LIXI message XML.
            
                Args:
                    message (:obj:`str`): Error string of the message.
                    test (:obj:`str`) : Test that caused the Error.
                    message_line (:obj:`str`): Line number in the input message.
                    message_location (:obj:`str`): Location xpath in the input message.
        
                """
        
                self.message = str.strip(message)
                self.test = test
                self.message_line = str(message_line)
                self.message_location = message_location        
        
        if schema!=None:
            schema_str = _LIXI.getInstance().fetch_xml_schema(
                schema_string=schema
            )
            schema_xsd = _etree.fromstring(schema_str)
            
        elif schema_path!=None:
            schema_str = _LIXI.getInstance().fetch_xml_schema(
                schema_path=schema_path,
            )
            schema_xsd = _etree.fromstring(schema_str)
        elif self.lixi_custom_version!=None:            
            schema_str = _LIXI.getInstance().fetch_xml_schema(
                custom_version=self.lixi_custom_version
            )
            schema_xsd = _etree.fromstring(schema_str)
        else:
            schema_str = _LIXI.getInstance().fetch_xml_schema(
                lixi_transaction_type=self.lixi_transaction_type,
                lixi_version=self.lixi_version
            ) 
            schema_xsd = _etree.fromstring(schema_str)

        validated_with = None
        if self.lixi_custom_version != None:
            schema_custom_version = schema_xsd.xpath(
                './xs:element[@name="Package"]/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXICustomVersion"]',
                namespaces=ns,
            )[0]
            if "fixed" not in schema_custom_version.attrib:
                raise LIXIInvalidSyntax(
                    "Version of the custom schema used is either incorrectly referenced in the message or does not specify the LIXICustomVersion. Please generate a new custom schema with lixi.get_custom_schema(). "
                )
            schema_custom_version = schema_custom_version.attrib["fixed"]

            validated_with = "LIXI Schema '" + schema_custom_version + "'."
            
        elif schema_path!=None or schema!=None:
            
            try:
                tr_type = schema_xsd.xpath(
                    './xs:element[@name="Package"]/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXITransactionType"]',
                    namespaces=ns,
                )[0]
                tr_type = tr_type.attrib["fixed"]
                
                i_version = schema_xsd.xpath(
                    './xs:element[@name="Package"]/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXIVersion"]',
                    namespaces=ns,
                )[0]
                i_version = i_version.attrib["fixed"]
                
                validated_with = (
                    "provided LIXI Schema '"
                    + tr_type
                    + " "
                    + i_version
                    + "'."
                )
            except:
                raise LIXIInvalidSyntax(
                    "Schema read failed. Invalid Schema. Missing LIXITransactionType or LIXIVersion. "
                )            
            
            schema_custom_version = schema_xsd.xpath(
                './xs:element[@name="Package"]/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]/xs:complexType/xs:attribute[@name="LIXICustomVersion"]',
                namespaces=ns,
            )
            if len(schema_custom_version)>0:
                if "fixed" in schema_custom_version[0].attrib:
                    schema_custom_version = schema_custom_version.attrib["fixed"]       
                    validated_with = "provided LIXI Custom Schema '" + schema_custom_version + "'."
                                    
                
        else:
            validated_with = (
                "LIXI Schema '"
                + self.lixi_transaction_type
                + " "
                + self.lixi_version
                + "'."
            )

        if self.file_type == "xml":
            schema_validation = _etree.XMLSchema(schema_xsd)
            result = schema_validation.validate(self.xml_package)

            if result:
                self.is_valid = True
                self.validation_message = (
                    "Message is valid, validated with " + validated_with
                )
                return True, "Message is valid, validated with " + validated_with, []
            else:
                
                list_of_error = []
                
                error = (
                    "Message read failed. Message is not valid when validated with "
                    + validated_with
                    + "\n"
                )
                error = error + "\nInvalid Assertions:"
                for scerror in schema_validation.error_log:
                    error = (
                        error
                        + "\n    Error On Line "
                        + str(scerror.line)
                        + ": "
                        + scerror.message
                    )
                    list_of_error.append(Error_Log(scerror.message, 'Validation', scerror.line, scerror.path))

                self.is_valid = False
                self.validation_message = error
                return False, error, list_of_error

        elif self.file_type == "json":

            # XML provides a better check especially around dates and checking cross references.
            # Methods for json validation which are close to xml validation exist but up to user's discretion.
            if self.xml_package == None:
                self.xml_package = _xml_to_json.to_xml(self.json_package, schema_xsd)

            schema_validation = _etree.XMLSchema(schema_xsd)
            result = schema_validation.validate(self.xml_package)

            if result:
                self.is_valid = True
                self.validation_message = (
                    "Message file is valid, validated with " + validated_with
                )
                return True, "Message file is valid, validated with " + validated_with, []
            else:
                xml_errors = ""
                list_of_error = []

                for scerror in schema_validation.error_log:
                    xml_errors = (
                        xml_errors
                        + "    Error On Line "
                        + "JSONX"
                        + ": "
                        + scerror.message
                        + "\n"
                    )
                    list_of_error.append(Error_Log(scerror.message, 'Validation', scerror.line, scerror.path))

                errors = str(xml_errors).split("\n")

                json_msg = self.json_string.split("\n")

                json_error_string = (
                    "Message read failed. Message is not valid when validated with "
                    + validated_with
                    + "\n"
                )
                json_error_string = json_error_string + "\nInvalid Assertions:"

                for error in errors:

                    element = re.search(r"Element '([a-zA-Z. ]*)'", error)
                    attribute = re.search(r"attribute '([a-zA-Z. ]*)'", error)

                    if attribute != None:
                        attribute_check = attribute.group(1)
                    else:
                        attribute_check = None

                    if element != None:
                        element_check = element.group(1)
                    else:
                        element_check = None

                    line_no = 1
                    for line in json_msg:
                        if attribute_check != None:
                            if attribute_check in line:
                                json_error_string += "\n" + error.replace(
                                    "JSONX", str(line_no)
                                )
                                break

                        elif element_check != None:
                            if element_check in line:
                                json_error_string += "\n" + error.replace(
                                    "JSONX", str(line_no)
                                )
                                break

                        line_no = line_no + 1

                self.is_valid = False
                self.validation_message = json_error_string
                return False, json_error_string, list_of_error

    def to_string(self):
        """Returns a string representation of the LIXI message.

        Returns:
            A pretty printed LIXI Message string.
        """

        if self.file_type == "xml":
            return str(
                _etree.tostring(self.xml_package, pretty_print=True).decode("utf-8")
            ).strip()
        elif self.file_type == "json":
            return str(
                _json.dumps(
                    self.json_package, sort_keys=True, indent=4, ensure_ascii=False
                )
            ).strip()

    def pretty_print(self):
        """Serialises to a string and prints the LIXI Message object.

        Result:
            Pretty prints a LIXI Message.
        """
        print(self.to_string())

    def save(self, output_path=None):
        """Serialises and saves a LIXI Message object to a file using the path provided.

        Args:
            output_path (:obj:`str`, optional): Path to write the schema paths list to. Defaults to None.
            
        Raises:
            LIXIResouceNotFoundError: If the path provided is not valid.    
        """

        string = self.to_string()

        if output_path == None:
            if self.file_type == "xml":
                output_path = "message_output.xml"
            elif self.file_type == "json":
                output_path = "message_output.json"

        self.__write__(
            "message_output.txt",
            output_path,
            string,
            "Message save failed. Can not store the schema at the specified folder.",
        )
