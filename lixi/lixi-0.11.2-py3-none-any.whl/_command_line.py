import os as _os

__version__ = str(_os.environ.get('test_version')) 


__all__ = [
    "set_credentials",
    "set_schema_folder",
    "get_schema_paths",
    "get_custom_schema",
    "get_json_schema",
    "get_xml_schema",
    "get_schema_documentation",
    "read_message",
]


if __name__ == "__main__":
    from _LIXI import (
        LIXI as _LIXI,
        LIXIValidationError
    )
    from _Message import Message as _Message
else:
    from lixi._LIXI import (
        LIXI as _LIXI,
        LIXIValidationError
    )
    from lixi._Message import Message as _Message


###################
## ENTRY POINTS
###################


def set_credentials(access, secret):
    """Sets the secret and access keys for a LIXI member, which would fetch a schema from the LIXI online repository. Used before doing any operations that require a schema. Both access key and secret key can be requested from LIXI admin. These are unique for an organization/member.  
    
    Args:
        access (:obj:`str`, required): A LIXI member's assigned access key. 
        secret (:obj:`str`, required): A LIXI member's assigned secret key. 
    
    Raises:
        LIXIInvalidSyntax: If 'access' is not specified or is not str. 
        LIXIInvalidSyntax: If 'secret' is not specified or is not str. 
    """

    _LIXI.getInstance().set_credentials(access, secret)


def set_schema_folder(folder_path, create_config=True, force_update=False):
    """Sets a directory path to fetch LIXI schemas from. Used before doing any operations that require a schema. Allows schema read from folder and a re-read of folder in case a file was added on runtime.   
    
    Args:
        folder_path (:obj:`str`, required): A path to a folder containing LIXI schema files.
        create_config (:obj:`bool`, required): A flag to indicate whether a folder read is required. Defaults to True.
        force_update (:obj:`bool`, optional): A flag to force update of the folder read. Defaults to False. 

    Raises: 
        LIXIInvalidSyntax: If folder_path is not specified.  
        LIXIResouceNotFoundError: If folder_path provided does not exist. 
    """
    _LIXI.getInstance().set_schema_path(folder_path, create_config, force_update)


def get_schema_paths(
    lixi_transaction_type=None,
    lixi_version=None,
    custom_version=None,
    schema_string=None,
    schema_path=None,
):
    """Fetches all of the elements paths of the LIXI schema provided as a Python List of paths. 

    Args:
        lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None. 
        lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided. 
        custom_version (:obj:`str`, optional): The version of the LIXI custom schema to be fetched. Usually a complete file name of the custom schema. Defaults to None. 
        schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None. 
        schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None. 

    Returns:
        A python list of all paths in the LIXI schema. 

    Raises:
        LIXIInvalidSyntax: Errors if inputs are not in the correct format. 
        LIXIResouceNotFoundError: Errors if inputs are not found. 
        LIXIValidationError: Validation errors for inputs. 
    """
    return _LIXI.getInstance().get_schema_paths(
        lixi_transaction_type,
        lixi_version,
        "xml",
        custom_version,
        schema_string,
        schema_path,
    )


def get_custom_schema(
    instructions_string=None,
    instructions_path=None,
    elements_array=None,
    lixi_transaction_type=None,
    lixi_version=None,
    schema_string=None,
    schema_path=None,
    output_name=None,
    output_folder=None,
    output_type="xml",
):
    """Generates a custom LIXI schema based on the given customization instructions source. This produced schema is based on the project (https://standards.lixi.org.au/lixi2/CustomisationByRestriction) that derives a subschema that only uses sub set of elements available in the full LIXI schema. This produced schema is a valid LIXI schema. 

    Args:
        instructions_string (:obj:`str`, optional): Customization instructions provided as a string. Defaults to None. 
        instructions_file (:obj:`str`, optional): Customization instructions provided as a path. Defaults to None.
        elements_array (:obj:`str`, optional): Customization paths to keep in an array. Defaults to None.
        lixi_transaction_type (:obj:`str`, optional): The transaction type of the LIXI schema to be fetched. Should be one of 'ACC', 'CAL', 'CDA', 'CNZ', 'DAS', 'LMI', 'SVC', 'VAL'. Defaults to None. 
        lixi_version (:obj:`str`, optional): The version of the LIXI schema to be fetched. Should be in the format of '2.6.24'. Defaults to None. Defaults to the latest version if only lixi_transaction_type is provided. 
        schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None. 
        schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None. 
        output_name (:obj:`str`, optional): String to set as a name of the custom schema. Defaults to None. 
        output_folder (:obj:`str`, optional): Path to write the produced lixi schema to. Defaults to None. 
        output_type (:obj:`str`, optional): The output type of the custom LIXI schema produced. Currently only accepts 'xml' and 'json'. Defaults to 'xml'. 

    Returns: 
        A customised LIXI schema as a string which can also be to the output folder specified. 

    Raises: 
        LIXIInvalidSyntax: Validation errors for the lixi version or transaction type. 
        LIXIResouceNotFoundError: If path provided does not exist. 
        LIXIValidationError: validation error in the customization instructions. 
    """

    return _LIXI.getInstance().generate_custom_schema(
        instructions_string,
        instructions_path,
        elements_array,
        lixi_transaction_type,
        lixi_version,
        schema_string,
        schema_path,
        output_name,
        output_folder,
        output_type,
    )


def get_json_schema(
    lixi_transaction_type=None,
    lixi_version=None,
    custom_version=None,
    schema_string=None,
    schema_path=None,
    output_path=None,
    return_annotated=False
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

    Result: 
        A string object of the LIXI JSON schema or saved to the output folder specified.  

    Raises:
        LIXIInvalidSyntax: Incorrect schema string/file fetched. 
        LIXIValidationError: Validation errors in the schema string/file fetched. 
        LIXIResouceNotFoundError: File not found or can't be written. 
    """

    return _LIXI.getInstance().fetch_json_schema(
        lixi_transaction_type,
        lixi_version,
        custom_version,
        schema_string,
        schema_path,
        output_path,
        return_annotated
    )


def get_xml_schema(
    lixi_transaction_type=None,
    lixi_version=None,
    custom_version=None,
    schema_string=None,
    schema_path=None,
    output_path=None,
    return_annotated=False
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

    Result:   
        A string object of the LIXI XML schema or saved to the output folder specified.    

    Raises:   
        LIXIInvalidSyntax: Incorrect schema string/file fetched.    
        LIXIValidationError: Validation errors in the schema string/file fetched.    
        LIXIResouceNotFoundError: File not found or can't be written.    
    """

    return _LIXI.getInstance().fetch_xml_schema(
        lixi_transaction_type,
        lixi_version,
        custom_version,
        schema_string,
        schema_path,
        output_path,
        return_annotated
    )

def get_schema_documentation(
    schema_string, 
    output_folder, 
    output_name
):
    """Generates a custom LIXI schema based on the given customization instructions source. This produced schema is based on the project (https://standards.lixi.org.au/lixi2/CustomisationByRestriction) that derives a subschema that only uses sub-set of elements available in the full LIXI schema. This produced schema is a valid LIXI schema.

    Args:
        schema_string (:obj:`str`, required): LIXI schema provided as a string.       
        output_folder (:obj:`str`, optional): Path to write the produced lixi schema documentation to. 
        output_name (:obj:`str`, optional): Name of the sub-folder that contains the documentation. 
    
    Returns:
        Outputs the custom documentation for a schema to the specified folder. 
    
    Raises:
        LIXIInvalidSyntax: If the provided schema_string is not a string or is unable to be read.
        LIXIResouceNotFoundError: If path provided does not exist.
    """

    _LIXI.getInstance().generate_schema_documentation(
        schema_string,
        output_folder,
        output_name,
    )

def read_message(
    message=None, message_path=None, file_type=None, schema_text=None, schema_path=None
):
    """Reads a LIXI message XML. 

    Args:
        message (:obj:`str`, optional): A LIXI Message provided as a string. Defaults to None. 
        message_path (:obj:`str`, optional) : A LIXI Message provided as a path. Defaults to None. 
        file_type (:obj:`str`, optional): The type of the input LIXI Message given. Defaults to 'xml'. DEPRECATED. But have kept it for later use if needed. 
        schema_string (:obj:`str`, optional): LIXI schema provided as a string. Defaults to None. 
        schema_path (:obj:`str`, optional): LIXI schema provided as a path. Defaults to None. 

    Returns: 
        A LIXI message instance. 

    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path. 
        LIXIInvalidSyntax: If the schema file is not well formed. 
        LIXIValidationError: If there are validation errors in the message file. 
    """

    # Read the Message
    lixi_message = _Message(message, message_path, file_type)

    # Validate the Message
    isvalid, result = lixi_message.validate(schema=schema_text, schema_path=schema_path)

    # A message is returned with error for LIXI API requirement
    if isvalid == False:
        raise LIXIValidationError(result, lixi_message)

    return lixi_message


# Setting default schema folder as starting folder
# _cwd = _os.getcwd()
# set_schema_folder(_cwd)
# print(_cwd)

###################
## TEST CODE
###################

# la_schema = get_customized_schema(instructions_path='C:/Users/compb/Documents/Git/lixi-pypi/tests/Customisation_Instruction_CAL.xml', schema_path='C:/Users/compb/Documents/Git/lixi-pypi/tests/LIXI-CAL-2_6_19-Annotated.xsd', output_name='Ammar_CAL', output_folder='C:/Users/compb/Documents/Git/lixi-pypi/tests')
# print('hallelujah')
