from lxml import isoschematron
from lxml import etree


def validate(xml_etree, schematron_etree):
    """ Validates a LIXI message against a Schematron business rules file.
    
    Args:
        xml_etree (:obj:`lxml.etree`, required): message to check provided as a Python Etree.
        schematron_etree (:obj:`lxml.etree`, required): Schematron rules provided as a Python Etree.
        error_log (:obj:`list`): Validation error object as a Python List.
    
    Result:
        result (:obj:`bool`): Indicates if validation was successful.
        message (:obj:`str`): Validation message.
    
    Raises:
        LIXIResouceNotFoundError: If the schema is not found at the schema path.
        LIXIInvalidSyntax: If the schema file is not well formed.
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

    schematron = isoschematron.Schematron(schematron_etree, store_report=True)
    validation_result = schematron.validate(xml_etree)

    report = schematron.validation_report

    if validation_result:
        return True, "Message schematron validation is successful.", None
    else:
        err_message = "Schematron validation failed."
        err_message += "\n\nInvalid Assertions:"
        
        list_of_error = []
        
        for fail in report.xpath(
            "//svrl:failed-assert",
            namespaces={"svrl": "http://purl.oclc.org/dsdl/svrl"},
        ):
            
            result =  xml_etree.xpath(str(fail.get("location")))
            if len(result)>0:
                line = str(result[0].sourceline)            
            else:
                line = "X"
            
            err_message = (
                err_message
                + "\n    Error On Line "
                + line
                + ": "
                + str(fail.getchildren()[0].text).strip()
            )
            
            list_of_error.append(Error_Log(fail.getchildren()[0].text, fail.get('test'), line, str(fail.get("location")) ))

        return False, err_message, list_of_error
