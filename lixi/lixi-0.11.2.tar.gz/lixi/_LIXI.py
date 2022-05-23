import pkg_resources as _pkg_resources
import os as _os
import io as _io
import json as _json
#import boto3 as _boto3
import glob as _glob
from lxml import etree as _etree
import time, re
from itertools import islice


ns = {
    "xs": "http://www.w3.org/2001/XMLSchema",
    "lx": "lixi.org.au/schema/appinfo_elements",
    "li": "lixi.org.au/schema/appinfo_instructions",
}

if __name__ == "_LIXI":
    import _path_functions, _jsonschema_functions, _customise_schema, _xslt_transform, _schema_documentation, _explode_schema
else:
    from lixi import (
        _path_functions,
        _jsonschema_functions,
        _customise_schema,
        _xslt_transform, 
        _schema_documentation,
        _explode_schema
    )


class LIXI(object):
    """Represents a LIXI Instance.
        
    The singleton class exists as a wrapper for all message manipulation functions the library is to provide.
    A LIXI schema is required because it is the underlying assumption that all LIXI members would 
    have a LIXI schema.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if LIXI.__instance == None:
            LIXI()
        return LIXI.__instance

    def __init__(self):
        """ Virtually private constructor. """

        if LIXI.__instance != None:
            print("This should not have run")
        else:

            self.schema_folder_path = (
                None  # _pkg_resources.resource_filename(__name__, 'schema/schema')
            )
            self.schema_index_dict = {}

            self.__S3_access = None
            self.__S3_secret = None

            self.current_transaction_type = None

            self.__schemas = {}
            self.__latest_versions = {}
            #self.__set_schema_latest_version__()
            
            self._lambda_check = False # used to clock all config files updates for lambda

            LIXI.__instance = self

    ####################
    ## HELPER FUNCTIONS
    ####################
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

        if _os.path.isdir(output_path):
            output_path = _os.path.join(output_path, default_name)

        try:
            with _io.open(output_path, "w+", encoding="utf-8") as out_file:
                out_file.write(data)
        except Exception as e:
            raise LIXIResouceNotFoundError(error_string)

    def __set_schema_latest_version__(self):
        """Helper function to set the latest version of the schema per transaction type. Relies on stored transformation files to obtain latest transaction version.

        Raises:
            LIXIResouceNotFoundError: If output path provided does not exist.
        """

        # Relies on stored transformation files to obtain latest transaction version. So these need to be updated every time there is a new version. Runs at program start.
        for filename in _glob.glob(
            _os.path.join(_pkg_resources.resource_filename(__name__, "xslts"), "*.zip")
        ):
            if "warnings" not in filename:
                filename = re.search(
                    r"LIXI-([a-zA-Z0-9_-]*).zip", filename.replace("LIXI", "", 1)
                ).group(1)

                split = filename.split("-")

                transaction_type = split[0]
                digit_1, digit_2, digit_3 = split[1].split("_")

                if transaction_type in self.__latest_versions:
                    old_version = self.__latest_versions[transaction_type]
                    olddigit_1, olddigit_2, olddigit_3 = old_version.split("_")

                    if int(digit_1) > int(olddigit_1):
                        self.__latest_versions[transaction_type] = split[1]
                    elif int(digit_1) == int(olddigit_1):
                        if int(digit_2) > int(olddigit_2):
                            self.__latest_versions[transaction_type] = split[1]
                        elif int(digit_2) == int(olddigit_2):
                            if int(digit_3) > int(olddigit_3):
                                self.__latest_versions[transaction_type] = split[1]

                else:
                    self.__latest_versions[transaction_type] = split[1]
    
    def __get_folder_latest_version__(self, lixi_transaction_type, actual_latest_schema_version):
        """Helper function to get the latest version of the schema per transaction type in a schema folder IF the latest actual latest schema does not exist locally. Needs to have a schema folder already specified.

        Args:
            lixi_transaction_type (:obj:`str`, required): Transaction type of the LIXI schema.
            actual_latest_schema_version (:obj:`str`, required): Latest version of the transation schema.

        Returns:
            A schema version string with format (X_X_X).
        """
        
        # Check if config file exists and use it
        if _os.path.exists(self.schema_folder_path + "/config.json"):
            with _io.open(
                self.schema_folder_path + "/config.json", encoding="utf-8"
            ) as json_index:
                schema_index_dict = _json.load(json_index)           
        
        list_of_schema_keys = schema_index_dict.keys()
        
        # If latest version is in folder proceed to return that.
        if 'LIXI-'+lixi_transaction_type+"-"+str(actual_latest_schema_version)+'-Annotated' in list_of_schema_keys:
            return actual_latest_schema_version
        
        # If not then try to derive the folder latest number and return.
        else:
            list_of_relevant_schema_keys = [str(key).replace('LIXI-'+lixi_transaction_type+'-','').replace("-Annotated","") for key in list_of_schema_keys if lixi_transaction_type in key and 'Custom' not in key]
            
            if len(list_of_relevant_schema_keys) == 0:
                return actual_latest_schema_version
            
            folder_latest_schema_version = None
            
            for key in list_of_relevant_schema_keys:
                if folder_latest_schema_version != None:
                    digit_1, digit_2, digit_3 = key.split("_")
                    
                    old_version = folder_latest_schema_version
                    olddigit_1, olddigit_2, olddigit_3 = old_version.split("_")

                    if int(digit_1) > int(olddigit_1):
                        folder_latest_schema_version = key 
                    elif int(digit_1) == int(olddigit_1):
                        if int(digit_2) > int(olddigit_2):
                            folder_latest_schema_version = key 
                        elif int(digit_2) == int(olddigit_2):
                            if int(digit_3) > int(olddigit_3):
                                folder_latest_schema_version = key 

                else:
                    folder_latest_schema_version = key                 
            
            return folder_latest_schema_version    
    
    
    def __create_schema_index_from_folder__(self, reset=False, create_config=True):
        """Helper function to create a config file (record of local schemas) from a folder.

        Args:
            reset (:obj:`boolean`, optional): A flag to force re-creation of the config file. Defaults to None.
            create_config (:obj:`boolean`, optional): Variable to force creation of config file for a schema folder. Defaults to True. Only for internal source.

        Raises:
            LIXIResouceNotFoundError: If schema folder path provided does not exist.
            LIXIInvalidSyntax: Validation errors for the lixi version or transaction type.
        """

        # if reset == false proceed to read from a pre-built config file.
        if _os.path.exists(self.schema_folder_path + "/config.json") and reset == False or self._lambda_check == True:
            with _io.open(
                self.schema_folder_path + "/config.json", encoding="utf-8"
            ) as json_index:
                self.schema_index_dict = _json.load(json_index)
        elif create_config and self._lambda_check==False:
            # read from the folder path and create a config file.

            if _os.path.exists(self.schema_folder_path) == False:
                raise LIXIResouceNotFoundError(
                    "Schema read failed. Schema folder path specified does not exist."
                )

            files = _glob.glob(_os.path.join(self.schema_folder_path, "*.xsd"))

            for filename in files:

                filename = filename.replace("\\", "/")
                f = _io.open(filename, mode="r", encoding="utf-8")
                
                if 'LIXI-Master-Schema.xsd' not in filename:
                
                    is_schema = False
                    read_string = ''
                    
                    # Read the first twenty-five lines of a schema to determine its transaction and version from annotation. Max is 25 lines.
                    for line in islice(f, 25):
                        read_string = read_string + line
                    
                    if "lx:schemadetail" in read_string:
                        schemadetail = re.search(
                            r'<lx:schemadetail(.*?)>', read_string
                        )
                        
                        if schemadetail != None:
                            schemadetail = schemadetail.group(1)
                            schemadetail = _etree.fromstring("<INFO "+schemadetail+">")
                            
                            if schemadetail.get('type') != "Master":
                                if schemadetail.get('type') == "Custom":
                                    schema_custom_version = schemadetail.get('version')
                                    annotated = schemadetail.get('annotation')
                                    is_schema = True
                                elif schemadetail.get('type') == "Transaction":
                                    schema_custom_version = None
                                    schema_transaction_type = schemadetail.get('transaction')
                                    schema_version = schemadetail.get('version')
                                    annotated = schemadetail.get('annotation')
                                    is_schema = True
    
                    # 1) only take a annotated schema 2) create a different key name so that filename won't matter 3) also if schema is custom version store that name 4) else store it as per transaction - version
                    if is_schema == True:
                        if schema_custom_version != None:
                            self.schema_index_dict[schema_custom_version] = filename
                        else:
                            if annotated == "Full":
                                self.schema_index_dict[
                                    "LIXI-"
                                    + schema_transaction_type
                                    + "-"
                                    + schema_version.replace(".", "_")
                                    + "-Annotated"
                                ] = filename
                            else:
                                self.schema_index_dict[
                                    "LIXI-"
                                    + schema_transaction_type
                                    + "-"
                                    + schema_version.replace(".", "_")
                                ] = filename                                
                
                f.close()
            # config file is stored. create_config will need to be turned off when used with AWS where write permissions are turned off.
            with _io.open(self.schema_folder_path + "/config.json", "wb+") as outfile:
                s = _json.dumps(
                    self.schema_index_dict, sort_keys=True, indent=4, ensure_ascii=False
                ).encode("utf-8")
                outfile.write(s)

        else:
            raise LIXIInvalidSyntax(
                "Schema read failed. Schema config file could not be created."
            )

    def __parse_xml_schema__(self, xsd_as_text, file_type, schema_internal_source):
        """Helper function to parse a LIXI XML schema from a string object. Important to note, will always return LIXI XML Etree Object.

        Args:
            xsd_as_text (:obj:`str`, required): LIXI schema provided as a string.
            file_type (:obj:`str`, optional): The type of the input LIXI schema given. Defaults to 'xml'. DEPRECATED. But have kept it for later use if needed.
            schema_internal_source (:obj:`str`, optional): A description of the source of the schema. Used for more descriptive error messages, and debugging.

        Returns:
             (
                'schema_output': A LIXI XML Etree object,
                'schema_transaction_type': The transaction type of the LIXI schema,
                'schema_version': The version of the transaction LIXI schema,
                'schema_custom_version': The custom version of the LIXI schema,
                'is_annotated' : Variable to indicate if the schema is annotated or not.
             )

        Raises:
            LIXIInvalidSyntax: Schema can not be read or type is not supported.
            LIXIInvalidSyntax: Missing Transaction Type.
            LIXIInvalidSyntax: Missing LIXI Version.
        """

        # Tries to parse the string as xml or json (converts back to xml schema since only xml is processed)
        passed = False
        schema_output = None

        if passed == False:
            try:
                parser = _etree.XMLParser(remove_blank_text=True)
                schema_output = _etree.fromstring(xsd_as_text, parser)
                passed = True
            except Exception as e:
                passed = False

        if passed == False:
            try:
                self.json_package = _json.loads(xsd_as_text)
                schema_output = _jsonschema_functions.convert_to_xml_schema(xsd_as_text)
                passed = True
            except Exception as e:
                passed = False

        # Parsing failed now we need better error messages
        if passed == False:

            error_message = ""

            if "<xs:schema" in xsd_as_text:
                try:
                    doc = etree.parse(filename_xml)
                except Exception as e:
                    error_message = e
            elif '"$schema"' in xsd_as_text:  ## is json
                try:
                    _json.loads(str(xsd_as_text))
                except Exception as e:
                    error_message = e

            raise LIXIInvalidSyntax(
                "Schema read failed. Schema from source '"
                + str(schema_internal_source)
                + "' can not be read or type is not supported.\n\nError Message:\n    "
                + str(error_message)
            )

        # Parsing suceeded now we need to extract schema info
        SchemaVersion = schema_output.xpath(
            './xs:element/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]',
            namespaces=ns,
        )[0]

        try:
            schema_transaction_type = SchemaVersion.xpath(
                './xs:complexType/xs:attribute[@name="LIXITransactionType"]',
                namespaces=ns,
            )[0]
            schema_transaction_type = schema_transaction_type.attrib["fixed"]
            self.current_transaction_type = schema_transaction_type
        except Exception as e:
            raise LIXIInvalidSyntax("Schema read failed. Missing Transaction Type.")

        try:
            schema_version = SchemaVersion.xpath(
                './xs:complexType/xs:attribute[@name="LIXIVersion"]', namespaces=ns
            )[0]
            schema_version = schema_version.attrib["fixed"]
        except Exception as e:
            raise LIXIInvalidSyntax("Schema read failed. Missing LIXI Version.")

        try:
            schema_custom_version = SchemaVersion.xpath(
                './xs:complexType/xs:attribute[@name="LIXICustomVersion"]',
                namespaces=ns,
            )[0]
            schema_custom_version = schema_custom_version.attrib["fixed"]
        except Exception as e:
            schema_custom_version = None
        
        try:
            annotated_val = schema_output.xpath(
                './xs:annotation/xs:appinfo/lx:schemadetail',
                namespaces=ns,
            )[0]
            annotated_val = annotated_val.attrib["annotation"]
            if annotated_val == "Minimal":
                is_annotated = False
            elif annotated_val == "Full":
                is_annotated = True
            
        except Exception as e:
            is_annotated = False        
        
        return (
            schema_output,
            schema_transaction_type,
            schema_version,
            schema_custom_version,
            is_annotated
        )

    def __read_path__(self, file_path, file_type="xml"):
        """Helper function to read a LIXI XML schema file from a path. Important to note, will always return LIXI XML Etree Object.

        Args:
            file_path (:obj:`str`, required): LIXI schema provided as a path.
            file_type (:obj:`str`, optional): The type of the input LIXI schema given. Defaults to 'xml'. DEPRECATED. But have kept it for later use if needed.

        Returns:
             (
                'schema_output': A LIXI XML Etree object,
                'schema_transaction_type': The transaction type of the LIXI schema,
                'schema_version': The version of the transaction LIXI schema,
                'schema_custom_version': The custom version of the LIXI schema,
                'is_annotated' : Variable to indicate if the schema is annotated or not.
             )

        Raises:
            LIXIResouceNotFoundError: Schema file not found at path.
        """

        # Read the file from path and display an error if not found.
        cwd = _os.getcwd()
        file_path = _os.path.join(cwd, file_path)

        if _os.path.exists(file_path) == True:
            f = _io.open(file_path, mode="r", encoding="utf-8")
            schema_string = f.read()
            f.close()
            (
                schema_output,
                schema_transaction_type,
                schema_version,
                schema_custom_version,
                is_annotated
            ) = self.__parse_xml_schema__(schema_string, file_type, file_path)

            return (
                schema_output,
                schema_transaction_type,
                schema_version,
                schema_custom_version,
                is_annotated
            )
        else:
            raise LIXIResouceNotFoundError(
                "Schema read failed. Schema file not found at the path "
                + str(file_path)
                + "."
            )

    def __load_schema__(
        self,
        lixi_transaction_type=None,
        lixi_version=None,
        file_type="xml",
        custom_version=None,
        schema_string=None,
        schema_path=None,
        create_config=True,
        return_annotated = False
    ):
        """Helper function to load a LIXI schema from multiple sources. Important to note, will always return LIXI XML Etree Object.

        Args:
            lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None.
            lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided.
            file_type (:obj:`str`, optional): The type of the input LIXI schema given. Defaults to 'xml'. DEPRECATED. But have kept it for later use if needed.
            custom_version (:obj:`str`, optional): The version of the LIXI custom schema to be fetched. Usually a complete file name of the custom schema. Defaults to None.
            schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None.
            schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None.
            create_config (:obj:`boolean`, optional): Variable to force creation of config file for a schema folder. Defaults to True. Only for internal source.
            return_annotated (:obj:`boolean`, optional): Variable to indicated if the returned schema should be annotated or not.

        Returns:
            A LIXI schema in the python Etree format.

        Raises:
            LIXIResouceNotFoundError: If no source of LIXI schema is provided.
            LIXIInvalidSyntax: Validation errors for the lixi version or transaction type.
            LIXIResouceNotFoundError: If path provided does not exist.
            LIXIValidationError: If path provided does not exist.
        """

        # Before loading the schema (source unknown at this point) make sure schema folder is read and a config file (record of local schemas) created.
        if (
            len(self.schema_index_dict) <= 0
            and self.schema_folder_path != None
            and create_config
        ):
            self.__create_schema_index_from_folder__(
                reset=False, create_config=create_config
            )

        # Read the schema into a Etree from the provided source.
        # Reading schema when it is passed as a string.
        if schema_string != None:
            (
                schema_output,
                schema_transaction_type,
                schema_version,
                schema_custom_version,
                is_annotated
            ) = self.__parse_xml_schema__(schema_string, file_type, "text")

            # Store it for later use if needed
            if schema_custom_version != None:
                self.__schemas[schema_custom_version] = schema_output
                return schema_output
            else:
                if is_annotated == True:
                    self.__schemas[
                        "LIXI-"
                        + schema_transaction_type
                        + "-"
                        + schema_version.replace(".", "_")
                        + "-Annotated"
                    ] = schema_output
                else:
                    self.__schemas[
                        "LIXI-"
                        + schema_transaction_type
                        + "-"
                        + schema_version.replace(".", "_")
                    ] = schema_output                     

                return schema_output

        # Reading schema when it is passed as a path.
        elif schema_path != None:
            (
                schema_output,
                schema_transaction_type,
                schema_version,
                schema_custom_version,
                is_annotated
            ) = self.__read_path__(schema_path, file_type)

            # Store it for later use if needed
            if schema_custom_version != None:
                self.__schemas[schema_custom_version] = schema_output
                return schema_output
            else:
                if is_annotated == True:
                    self.__schemas[
                        "LIXI-"
                        + schema_transaction_type
                        + "-"
                        + schema_version.replace(".", "_")
                        + "-Annotated"
                    ] = schema_output
                else:
                    self.__schemas[
                        "LIXI-"
                        + schema_transaction_type
                        + "-"
                        + schema_version.replace(".", "_")
                    ] = schema_output                     

                return schema_output

        # Reading a custom schema version. HAS to be read before reading schema from transaction and version because all custom schemas have these two fields populated so there is a risk of fetching the transaction schema when a custom schema is needed.
        elif custom_version != None:

            # If custom schema stored in local variable use that
            if custom_version in self.__schemas:
                return self.__schemas[custom_version]

            # Else look for it locally
            if self.schema_folder_path != None:

                # Update folder just in case custom schema was recently generated and stored
                if custom_version not in self.schema_index_dict:
                    self.__create_schema_index_from_folder__(
                        reset=True, create_config=create_config
                    )

                if custom_version in self.schema_index_dict:
                    filepath = self.schema_index_dict[custom_version]

                    (
                        schema_output,
                        schema_transaction_type,
                        schema_version,
                        schema_custom_version,
                        is_annotated
                    ) = self.__read_path__(filepath, file_type)

                    self.__schemas[schema_custom_version] = schema_output

                    return self.__schemas[schema_custom_version]
                else:
                    raise LIXIResouceNotFoundError(
                        "Schema read failed. Custom schema file "+ custom_version+ " not found in the schema folder."
                    )
            else:
                raise LIXIResouceNotFoundError(
                    "Schema read failed. Can not read custom schema file '"
                    + custom_version
                    + "'. Please set a schema folder with lixi.set_schema_folder()."
                )

        # Reading a schema with lixi transaction schema and version.
        elif lixi_transaction_type != None and lixi_version != None:
            
            schema_name_annotated = (
                "LIXI-"
                + lixi_transaction_type
                + "-"
                + lixi_version.replace(".", "_")
                + "-Annotated"
            )
            schema_name_unannotated = (
                "LIXI-"
                + lixi_transaction_type
                + "-"
                + lixi_version.replace(".", "_")
            )                
            self.current_transaction_type = lixi_transaction_type

            # Look for schema in stored variable
            
            if schema_name_annotated in self.__schemas and schema_name_unannotated in self.__schemas:
                if return_annotated == True:
                    return self.__schemas[schema_name_annotated]
                elif return_annotated == False:
                    return self.__schemas[schema_name_unannotated]
            elif schema_name_annotated in self.__schemas and schema_name_unannotated not in self.__schemas:
                if return_annotated == True:
                    return self.__schemas[schema_name_annotated]
                elif return_annotated == False:
                    return self.__schemas[schema_name_annotated]                    
            elif schema_name_annotated not in self.__schemas and schema_name_unannotated in self.__schemas:
                if return_annotated == True:
                    schema_name = schema_name_annotated
                elif return_annotated == False:
                    return self.__schemas[schema_name_unannotated]            
            elif schema_name_annotated not in self.__schemas and schema_name_unannotated not in self.__schemas:
                if return_annotated == True:
                    schema_name = schema_name_annotated
                elif return_annotated == False:
                    schema_name = schema_name_unannotated           
                    

            if self.schema_folder_path != None:

                
                if schema_name not in self.schema_index_dict:
                    # Update folder just in case custom schema was recently generated and stored
                    if create_config:
                        self.__create_schema_index_from_folder__(
                            reset=True, create_config=create_config
                        )

                if schema_name in self.schema_index_dict and create_config:
                    filepath = self.schema_index_dict[schema_name]
                    (
                        schema_output,
                        schema_transaction_type,
                        schema_version,
                        schema_custom_version,
                        is_annotated
                    ) = self.__read_path__(filepath, file_type)

                    self.__schemas[schema_name] = schema_output

                    return self.__schemas[schema_name]
                
                elif schema_name_annotated in self.schema_index_dict and create_config:
                    filepath = self.schema_index_dict[schema_name_annotated]
                    (
                        schema_output,
                        schema_transaction_type,
                        schema_version,
                        schema_custom_version,
                        is_annotated
                    ) = self.__read_path__(filepath, file_type)

                    self.__schemas[schema_name_annotated] = schema_output

                    return schema_output                
                else:
                    anno = ''
                    if return_annotated == True:
                        anno = 'Annotated'
                    
                    raise LIXIResouceNotFoundError(
                        "Schema read failed. Schema file "+ lixi_transaction_type+" "+ lixi_version+" "+anno+" not found in the schema folder."
                    )

            # Download the schema if credentials are provided
            #if self.__S3_access != None and self.__S3_secret != None:
                #session = _boto3.Session(
                    #aws_access_key_id=self.__S3_access,
                    #aws_secret_access_key=self.__S3_secret,
                #)

                #if file_type == "xml":
                    #schema_name2 = schema_name + ".xsd"

                #s3 = session.resource("s3")
                #obj = s3.Object("lixi-schema", schema_name2)
                #string_data = obj.get()["Body"].read().decode("utf-8")

                #(
                    #schema_output,
                    #schema_transaction_type,
                    #schema_version,
                    #schema_custom_version,
                    #is_annotated
                #) = self.__parse_xml_schema__(string_data, file_type, "S3")

                #self.__schemas[schema_name] = schema_output

                #return self.__schemas[schema_name]

            if (
                self.__S3_access == None
                and self.__S3_secret == None
                and self.schema_folder_path == None
            ):
                raise LIXIResouceNotFoundError(
                    "Schema read failed. Can not read schema file '"
                    + lixi_transaction_type
                    + " "
                    + lixi_version
                    + " "
                    + 'Annotated' if return_annotated == True else ''
                    + "'. Please set a schema folder with lixi.set_schema_folder()."
                )

        else:
            raise LIXIResouceNotFoundError(
                "Schema read failed. Please specify a LIXI Schema source (String, Path to LIXI schema, Path to a folder that contains a LIXI schema or LIXI schema S3 credentials)."
            )

    ###################
    ## ENTRY POINTS
    ###################
    #def set_credentials(self, access, secret):
        #"""Sets the secret and access keys for a LIXI member, which would enable a schema to be fetched from the LIXI online repository. 
        #Both access key and secret key can be requested from LIXI admin. These are unique for an organization/member. 
        
        #Args:
            #access (:obj:`str`, required): A LIXI member's assigned access key.
            #secret (:obj:`str`, required): A LIXI member's assigned secret key.
        
        #Raises:
            #LIXIInvalidSyntax: If 'access' is not specified or is not str.
            #LIXIInvalidSyntax: If 'secret' is not specified or is not str.
        #"""

        #if access != None and secret != None:

            #if type(access).__name__ == "str" and type(secret).__name__ == "str":
                #self.__S3_access = access
                #self.__S3_secret = secret
            #else:
                #raise LIXIInvalidSyntax("Parameter provided is not a string.")
        #else:
            #raise LIXIInvalidSyntax("Required parameter not specified.")

    def set_schema_path(self, schemapath, create_config=True, force_update=False, lambda_check=False):
        """Sets a directory path to fetch LIXI schemas from. Used before doing any operations that require a schema. Allows schema read from folder and a re-read of folder in case a file was added on runtime.  
    
        Args:
            folder_path (:obj:`str`, required): A path to a folder containing LIXI schema files.
            create_config (:obj:`bool`, required): A flag to indicate whether a folder read is required.
            force_update (:obj:`bool`, required): A flag to force folder read.
        
        Raises:
            LIXIInvalidSyntax: If path is not specified.
            LIXIResouceNotFoundError: If path provided does not exist.
        """

        if schemapath != None:
            if _os.path.exists(schemapath):
                self.schema_folder_path = str(schemapath)
                self.__create_schema_index_from_folder__(reset = force_update, create_config = create_config)
                self._lambda_check = lambda_check
            else:
                raise LIXIResouceNotFoundError("Schema folder path is incorrect.")
        else:
            raise LIXIResouceNotFoundError("Schema folder path not specified.")

    def get_schema_latest_version(self, lixi_transaction_type):
        """Gets the latest version number of a LIXI transation schema released, or the latest version number in the folder if a schema folder path has been previously provided.

        Args:
            lixi_transaction_type (:obj:`str`, required): Transaction type of the LIXI schema.

        Returns:
            A schema version string with format (X_X_X).

        Raises:
            LIXIInvalidSyntax: Invalid transaction type provided.
        """
        latest_version_of_schema = None 
        
        #if lixi_transaction_type == "ACC":
            #latest_version_of_schema = self.__latest_versions["ACC"]
        #elif lixi_transaction_type == "CAL":
            #latest_version_of_schema = self.__latest_versions["CAL"]
        #elif lixi_transaction_type == "CDA":
            #latest_version_of_schema = self.__latest_versions["CDA"]
        #elif lixi_transaction_type == "CNZ":
            #latest_version_of_schema = self.__latest_versions["CNZ"]
        #elif lixi_transaction_type == "DAS":
            #latest_version_of_schema = self.__latest_versions["DAS"]
        #elif lixi_transaction_type == "LMI":
            #latest_version_of_schema = self.__latest_versions["LMI"]
        #elif lixi_transaction_type == "SVC":
            #latest_version_of_schema = self.__latest_versions["SVC"]
        #elif lixi_transaction_type == "VAL":
            #latest_version_of_schema = self.__latest_versions["VAL"]
        #else:
            #raise LIXIInvalidSyntax(
                #"Schema read failed. Invalid transaction type provided."
            #)
        
        
        if lixi_transaction_type in self.__latest_versions:
            return self.__latest_versions[lixi_transaction_type]
        else:
            if self.schema_folder_path != None:
            
                version = self.__get_folder_latest_version__(lixi_transaction_type, latest_version_of_schema)
            
                if lixi_transaction_type not in self.__latest_versions:
                    self.__latest_versions[lixi_transaction_type] = version
            
                return version
            else:
                raise LIXIInvalidSyntax(
                    "Schema read failed. Schema folder path not set."
                )                
        #else:
            #return latest_version_of_schema

    def fetch_json_schema(
        self,
        lixi_transaction_type=None,
        lixi_version=None,
        custom_version=None,
        schema_string=None,
        schema_path=None,
        output_path=None,
        return_annotated = False,
        exploded = False        
    ):
        """Fetches a LIXI JSON schema dict object or converts from an LIXI XML schema.

        Args:
            lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None.
            lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided.
            custom_version (:obj:`str`, optional): The version of the LIXI custom schema to be fetched. Usually a complete file name of the custom schema. Defaults to None.
            schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None.
            schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None.
            output_path (:obj:`str`, optional): Path to write the fetched lixi schema to. Defaults to None.
            return_annotated (:obj:`boolean`, optional): Variable to indicated if the returned schema should be annotated or not.
            exploded (:obj:`boolean`, optional): Variable to indicate if the returned schema should be exploded or not.
            
            
        Result:
            A Python dict object of the schema or saved to the output folder specified. 
    
        Raises:
            LIXIInvalidSyntax: Incorrect schema string/file fetched.
            LIXIValidationError: Validation errors in the schema string/file fetched.
            LIXIResouceNotFoundError: File not found or can't be written.
        """
        # Make sure schema is annotated if exploded set to true
        if exploded==True:
            return_annotated = True
            
        # Determine which source is given
        output_schema = None

        if (
            lixi_transaction_type == None
            and custom_version == None
            and schema_string == None
            and schema_path == None
        ):
            raise LIXIInvalidSyntax(
                "Fetch schema failed. Fetch parameters not specified."
            )

        # Custom schema is done first to avoid fetching un custom schema based on transaction and version number
        if custom_version != None:
            output_xml_schema = self.__load_schema__(custom_version=custom_version)
            

        # Fetch based on transaction type and version
        elif lixi_version != None or lixi_transaction_type != None:
            if lixi_transaction_type == None:
                raise LIXIInvalidSyntax(
                    "Fetch schema failed. Transaction type parameter not specified."
                )

            if lixi_version == None:
                if self.schema_folder_path == None:
                    raise LIXIResouceNotFoundError(
                        "Please specify a Transaction LIXI Version or set the schema folder with lixi.set_schema_folder() to fetch the latest in the schema folder.\n"
                        + str(error_message)
                    )
                else:
                    lixi_version = self.get_schema_latest_version(lixi_transaction_type)

            output_xml_schema = self.__load_schema__(
                lixi_transaction_type=lixi_transaction_type, lixi_version=lixi_version, return_annotated=return_annotated
            )
            

        # Fetch based on string or path
        elif schema_string != None or schema_path != None:

            if schema_path != None:
                output_xml_schema = self.__load_schema__(schema_path=schema_path, return_annotated=return_annotated)
            else:
                output_xml_schema = self.__load_schema__(schema_string=schema_string, return_annotated=return_annotated)

            
            
        # Explode the schema if flag set to True
        if exploded==True:
            output_xml_schema = _explode_schema.main(output_xml_schema)
            
        # Convert into JSON
        output_schema = _jsonschema_functions.convert_to_json_schema(
            output_xml_schema
        )        
            
        # Output the schema to a file or return object
        if output_path == None:
            return _json.dumps(
                        output_schema, sort_keys=True, indent=4, ensure_ascii=False
                    )
        else:
            self.__write__(
                "fetched_json_schema_output.json",
                output_path,
                str(
                    _json.dumps(
                        output_schema, sort_keys=True, indent=4, ensure_ascii=False
                    )
                ).strip(),
                "Fetch schema failed. Can not store the schema at the specified folder.",
            )

            return output_schema

    def fetch_xml_schema(
        self,
        lixi_transaction_type=None,
        lixi_version=None,
        custom_version=None,
        schema_string=None,
        schema_path=None,
        output_path=None,
        return_annotated = False,
        exploded = False
    ):
        """Fetches a LIXI XML schema Etree object or converts from an LIXI JSON schema.

        Args:
            lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None.
            lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided.
            custom_version (:obj:`str`, optional): The version of the LIXI custom schema to be fetched. Usually a complete file name of the custom schema. Defaults to None.
            schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None.
            schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None.
            output_path (:obj:`str`, optional): Path to write the fetched lixi schema to. Defaults to None.
            return_annotated (:obj:`boolean`, optional): Variable to indicated if the returned schema should be annotated or not.
            exploded (:obj:`boolean`, optional): Variable to indicate if the returned schema should be exploded or not.
            
        Result:
            A Python Etree object of the schema or saved to the output folder specified. 
    
        Raises:
            LIXIInvalidSyntax: Incorrect schema string/file fetched.
            LIXIValidationError: Validation errors in the schema string/file fetched.
            LIXIResouceNotFoundError: File not found or can't be written.
        """
        
        # Make sure schema is annotated if exploded set to true
        if exploded==True:
            return_annotated = True
            
        # Determine which source is given
        output_schema = None

        if (
            lixi_transaction_type == None
            and custom_version == None            
            and schema_string == None
            and schema_path == None
        ):
            raise LIXIInvalidSyntax(
                "Fetch schema failed. Fetch parameters not specified."
            )

        # Custom schema is done first to avoid fetching un custom schema based on transaction and version number
        if custom_version != None:
            output_schema = self.__load_schema__(custom_version=custom_version)

        # Fetch based on transaction type and version
        elif lixi_version != None or lixi_transaction_type != None:
            if lixi_transaction_type == None:
                raise LIXIInvalidSyntax(
                    "Fetch schema failed. Transaction type parameter not specified."
                )

            if lixi_version == None:
                if self.schema_folder_path == None:
                    raise LIXIResouceNotFoundError(
                        "Please specify a Transaction LIXI Version or set the schema folder with lixi.set_schema_folder() to fetch the latest in the schema folder.\n"
                        + str(error_message)
                    )
                else:                
                    lixi_version = self.get_schema_latest_version(lixi_transaction_type)

            output_schema = self.__load_schema__(
                lixi_transaction_type=lixi_transaction_type, lixi_version=lixi_version, return_annotated=return_annotated
            )

        # Fetch based on string or path
        elif schema_string != None or schema_path != None:

            if schema_path != None:
                output_schema = self.__load_schema__(schema_path=schema_path, return_annotated=return_annotated)
            else:
                output_schema = self.__load_schema__(schema_string=schema_string, return_annotated=return_annotated)
        
        # Explode the schema if flag set to True
        if exploded==True:
            output_schema = _explode_schema.main(output_schema)
                
        # Output the schema to a file or return object
        if output_path == None:
            return _etree.tostring(output_schema, pretty_print=True).decode("utf-8")
        else:
            self.__write__(
                "fetched_xml_schema_output.xsd",
                output_path,
                str(
                    _etree.tostring(output_schema, pretty_print=True).decode("utf-8")
                ).strip(),
                "Fetch schema failed. Can not store the schema at the specified folder.",
            )

            return output_schema

    def get_schema_paths(
        self,
        lixi_transaction_type=None,
        lixi_version=None,
        file_type="xml",
        custom_version=None,
        schema_string=None,
        schema_path=None,
        exploded = False
    ):
        """Fetches all of the elements paths of the LIXI schema provided as a Python List of paths. 

        Args:
            lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None.
            lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided.
            custom_version (:obj:`str`, optional): The version of the LIXI custom schema to be fetched. Usually a complete file name of the custom schema. Defaults to None.
            schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None.
            schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None.
            exploded (:obj:`bool`, optional): Variable to indicate if the returned schema should be exploded or not. 
    
        Returns:
            A python list of all paths in the LIXI schema.
    
        Raises:
            LIXIInvalidSyntax: Validation errors for the lixi version or transaction type.
            LIXIResouceNotFoundError: If path provided does not exist.
            LIXIValidationError: If path provided does not exist.
        """

        # Get the latest version of the transactiontion schema if required.
        if lixi_transaction_type != None and lixi_version == None:
            
            if self.schema_folder_path == None:
                raise LIXIResouceNotFoundError(
                    "Please specify a Transaction LIXI Version or set the schema folder with lixi.set_schema_folder() to fetch the latest schema in the schema folder, to obtain schema paths.\n"
                    + str(error_message)
                )
            else:            
            
                lixi_version = str(
                    self.get_schema_latest_version(lixi_transaction_type)
                ).replace("_", ".")

        # Load the required version of the transaction schema.
        schema = self.__load_schema__(
            lixi_transaction_type,
            lixi_version,
            file_type,
            custom_version,
            schema_string,
            schema_path,
            True,
            True
        )

        # Generate schema paths.
        if exploded:
            return _path_functions.get_exploded_paths_for_schema_elements(schema)
        else:
            return _path_functions.get_paths_for_schema_elements(schema)

    def generate_custom_schema(
        self,
        instructions=None,
        instructions_path=None,
        elements_array=None,
        lixi_transaction_type=None,
        lixi_version=None,
        schema_string=None,
        schema_path=None,
        output_name=None,
        output_folder=None,
        output_type="xml",
        output_instructions=False,
    ):
        """Generates a custom LIXI schema based on the given customization instructions source. This produced schema is based on the project (https://standards.lixi.org.au/lixi2/CustomisationByRestriction) that derives a subschema that only uses sub set of elements available in the full LIXI schema. This produced schema is a valid LIXI schema.

        Args:
            instructions (:obj:`str`, optional): Customization instructions provided as a string. Defaults to None.
            instructions_file (:obj:`str`, optional): Customization instructions provided as a path. Defaults to None.
            elements_array (:obj:`str`, optional): Customization paths to keep in an array. Defaults to None.
            lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None.
            lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided.
            schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None.
            schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None.
            output_name (:obj:`str`, optional): String to set as a name of the custom schema. Defaults to None.
            output_folder (:obj:`str`, optional): Path to write the produced lixi schema to. Defaults to None.
            output_type (:obj:`str`, optional): The output type of the custom LIXI schema produced. Currently only accepts 'xml' and 'json'.
            output_instructions (:obj:`boolean`, optional): A flag to indicate whether a customization instructions need to be saved to a path. Must have the output folder path set. Defaults to False. 
        
        Returns:
            A customised LIXI schema as a string which can also be to the output folder specified.
        
        Raises:
            LIXIInvalidSyntax: Validation errors for the lixi version or transaction type.
            LIXIResouceNotFoundError: If path provided does not exist.
            LIXIValidationError: validation error in the customization instructions.
        """
        # Read the instructions file
        if instructions != None or instructions_path != None:

            if instructions_path != None:
                if _os.path.exists(instructions_path) == True:
                    instructions = _etree.parse(instructions_path)
                    instructions = instructions.getroot()
                    instructions = _etree.tostring(instructions).decode("utf-8")
                else:
                    raise LIXIResouceNotFoundError(
                        "Customised schema generation failed. Instructions file not found at the specified path."
                    )

            if (
                lixi_transaction_type == None
                and schema_string == None
                and schema_path == None
            ):
                transactiontype = re.search(
                    r'LIXITransactionType="([A-Z]*)"', instructions
                )
                try:
                    lixi_transaction_type = transactiontype.group(1)
                except:
                    raise LIXIInvalidSyntax(
                        "Customised schema generation failed. Instructions file does not have the transaction type specified."
                    )                    
                
            if lixi_transaction_type != None and lixi_version==None:
                if self.schema_folder_path == None:
                    raise LIXIResouceNotFoundError(
                        "Please specify a Transaction LIXI Version or set the schema folder with lixi.set_schema_folder() to fetch the latest schema in the schema folder, to obtain a customised schema.\n"
                        + str(error_message)
                    )
                else:                
                    lixi_version = str(
                        self.get_schema_latest_version(lixi_transaction_type)
                    ).replace("_", ".")

            # Has to be XML and has to be transaction hence custom is None
            schema = self.__load_schema__(
                lixi_transaction_type,
                lixi_version,
                "xml",
                None,
                schema_string,
                schema_path,
                True,
                True
            )

        # Read the csv text/file. Assupmtion for csv text is 'Package,Package.Content,..........'
        elif elements_array != None:
            
            if lixi_transaction_type != None and lixi_version==None:
                if self.schema_folder_path == None:
                    raise LIXIResouceNotFoundError(
                        "Please specify a Transaction LIXI Version or set the schema folder with lixi.set_schema_folder() to fetch the latest schema in the schema folder, to obtain a customised schema.\n"
                        + str(error_message)
                    )
                else:                  
                
                    lixi_version = str(
                        self.get_schema_latest_version(lixi_transaction_type)
                    ).replace("_", ".")            
            
            schema = self.__load_schema__(
                lixi_transaction_type,
                lixi_version,
                "xml",
                None,
                schema_string,
                schema_path,
                True,
                True
            )  # Has to be XML and has to be transaction hence custom is None
            
            if len(elements_array)>0:
                include_elements_list = elements_array
                include_elements_list = [elem.strip() for elem in elements_array]
            else:
                raise LIXIResouceNotFoundError(
                    "Array provided for customization is not populated. Please iclude paths in the array for schema customisation.\n"
                    + str(error_message)
                )                

            #if csv_path != None:
                #if _os.path.exists(csv_path) == True:
                    #f = _io.open(csv_path, mode="r", encoding="utf-8")
                    #csv_text = f.read()
                    #f.close()
                #else:
                    #raise LIXIResouceNotFoundError(
                        #"Customised schema generation failed. CSV file not found at the specified path."
                    #)

            ## Since CSV is a elements-to-include list, derive a instructions file based on that.
            #if len(csv_text.split("\n")) > 0:
                #temp_list = csv_text.split("\n")            
            #elif len(csv_text.split(",")) > 0:
                #temp_list = csv_text.replace("\n", "").split(",")
            
            #include_elements_list = [elem.strip() for elem in temp_list]

            message_paths = _path_functions.get_paths_for_elements(
                paths_list=include_elements_list, schema=schema
            )
            schema_paths = _path_functions.get_paths_for_schema_elements(schema)

            instructions = _path_functions.get_blacklist_paths_for_customization(
                self.current_transaction_type, message_paths, schema_paths
            )

        
        
        # Generate the customised schema as string
        (
            customised_schema,
            output_name,
        ) = _customise_schema.execute_customisation_instructions(
            schema, instructions, output_name
        )
        
        # Generate customization instructions if flag set to true
        if output_instructions==True:
            if output_folder!=None:
                cust_output_path = _os.path.join(output_folder, output_name + ".xml")
            else:
                cust_output_path = _os.path.join(_os.getcwd(), output_name + ".xml")
                
            self.__write__(
                "customised_instructions_output.xsd",
                cust_output_path,
                instructions,
                "Customised schema instructions generation failed. Can not store the produced custom schema at the specified folder.",
            )                
        
        # Setting ouput type
        if output_type == "xml":
            output = customised_schema  ##xsd
        elif output_type == "json":
            output = _jsonschema_functions.convert_to_json_schema(
                _etree.fromstring(customised_schema)
            )
            output = _json.dumps(output, sort_keys=True, indent=4, ensure_ascii=False)

        # Output as required.
        if output_folder == None:
            return output
        else:
            if output_type == "xml":
                output_path = _os.path.join(output_folder, output_name + ".xsd")
            elif output_type == "json":
                output_path = _os.path.join(output_folder, output_name + ".json")

            self.__write__(
                "custom_schema_output.xsd",
                output_path,
                output,
                "Customised schema generation failed. Can not store the produced custom schema at the specified folder.",
            )

            return output

    def generate_schema_documentation(
        self,
        schema_string, 
        output_folder = None, 
        output_name = None,
        glossary_string = None
    ):
        """Generates a custom LIXI schema based on the given customization instructions source. This produced schema is based on the project (https://standards.lixi.org.au/lixi2/CustomisationByRestriction) that derives a subschema that only uses sub set of elements available in the full LIXI schema. This produced schema is a valid LIXI schema.

        Args:
            schema_string (:obj:`str`, required): LIXI schema provided as a string.
            output_folder (:obj:`str`, required): Path to write the produced lixi schema documentation to. If output_path is specified as None, a zip bytes file is returned.
            output_name (:obj:`str`, optional): Name of the sub-folder that contains the documentation. Defaults to None.      
            glossary_string (:obj:`str`, optional): LIXI Glossary update provided as a string. Defaults to None.
        
        Returns:
            Outputs the custom documentation for a schema to the specified folder. 
        
        Raises:
            LIXIInvalidSyntax: If the provided schema_string is not a string or is unable to be read.
            LIXIResouceNotFoundError: If path provided does not exist.
        """
        
        json_schema_string = None 
        
        if output_folder!=None:
            if _os.path.exists(output_folder) == False:
                raise LIXIResouceNotFoundError(
                    "Schema documentation creation failed. Schema folder path specified does not exist."
                )            
        
        if type(schema_string) != str:
            raise LIXIInvalidSyntax(
                "Schema documentation creation failed. Schema provided is not in a string format or can not be read."
            )            
        
        if '"$schema"' in schema_string:  ## is json
            json_schema_string = schema_string
            xml_schema_string = self.fetch_xml_schema(schema_string = schema_string, return_annotated=True)
            
            if output_name == None:
                sv = _json.loads(json_schema_string)
                
                if '@LIXICustomVersion' in sv['properties']['Package']['properties']['SchemaVersion']['properties']:
                    if 'enum' in sv['properties']['Package']['properties']['SchemaVersion']['properties']['@LIXICustomVersion']:
                        custom = sv['properties']['Package']['properties']['SchemaVersion']['properties']['@LIXICustomVersion']['enum'][0]
                        output_name = custom
                    else:
                        version = sv['properties']['Package']['properties']['SchemaVersion']['properties']['@LIXIVersion']['enum'][0]
                        trxn = sv['properties']['Package']['properties']['SchemaVersion']['properties']['@LIXITransactionType']['enum'][0]
                        output_name = str('LIXI-'+trxn+'-'+version.replace('.','_')+'-Annotated')                        
                else:
                    version = sv['properties']['Package']['properties']['SchemaVersion']['properties']['@LIXIVersion']['enum'][0]
                    trxn = sv['properties']['Package']['properties']['SchemaVersion']['properties']['@LIXITransactionType']['enum'][0]
                    output_name = str('LIXI-'+trxn+'-'+version.replace('.','_')+'-Annotated')
            
        elif "<xs:schema" in schema_string:
            xml_schema_string = schema_string
            
            if output_name == None:
                etr = _etree.fromstring(xml_schema_string)
                sv = etr.xpath('./xs:element/xs:complexType/xs:sequence/xs:element[@name="SchemaVersion"]', namespaces=ns)[0]        
                
                if len(sv.xpath('./xs:complexType/xs:attribute[@name="LIXICustomVersion"]', namespaces=ns))>0:
                    custom = sv.xpath('./xs:complexType/xs:attribute[@name="LIXICustomVersion"]', namespaces=ns)[0].attrib["fixed"]
                    output_name = custom
                else:
                    version = sv.xpath('./xs:complexType/xs:attribute[@name="LIXIVersion"]', namespaces=ns)[0].attrib["fixed"]
                    trxn = sv.xpath('./xs:complexType/xs:attribute[@name="LIXITransactionType"]', namespaces=ns)[0].attrib["fixed"]
                    output_name = str('LIXI-'+trxn+'-'+version.replace('.','_')+'-Annotated')
            
        else:
            raise LIXIInvalidSyntax(
                "Schema documentation creation failed. Schema provided can not be read."
            )
        
        if 'annotation="Full"' not in xml_schema_string: 
            raise LIXIInvalidSyntax(
                "Schema documentation creation failed. Schema provided is not fully annotated, as required."
            )        
        
        schema_doc_zip = None
        try:
            schema_doc_zip =  _schema_documentation.create_schema_documentation(xml_schema_string, json_schema_string, output_folder, output_name, glossary_string)
        except Exception as e:    
            raise LIXIInvalidSyntax(
                "Schema documentation creation failed.\n\nError Message:\n    "
                + str(e)
            )
        
        return schema_doc_zip 

#################
## ERROR CLASSES
#################
class LIXIResouceNotFoundError(Exception):
    def __init__(self, message):
        super().__init__("" + message)


class LIXIInvalidSyntax(Exception):
    def __init__(self, message):
        super().__init__("" + message)


class LIXIValidationError(Exception):
    def __init__(self, message, message_instance=None, error_log=None):

        super().__init__(message)
        self.message_instance = message_instance
        self.error_log = error_log
