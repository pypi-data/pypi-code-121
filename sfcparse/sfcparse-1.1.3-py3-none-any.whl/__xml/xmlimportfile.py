# xmlimportfile
#########################################################################################################
# Imports
import xml.etree.ElementTree as __xml_etree
from ..error import SfcparseError

# Exception for Module
class _Xmlimportfile: 
    class xmlimportfile(SfcparseError): __module__ = SfcparseError.set_module_name()


#########################################################################################################
# Import xml file
def xmlimportfile(filename: str) -> __xml_etree.Element:
    """
    Imports xml data from a file.

    Returns a xml Parsed Element obj with the root. Assign the output to var

    Enter xml file location as str to import.

    [Example Use]

    xmlimportfile('path/to/filename.xml')

    This is using the native xml library via etree shipped with the python standard library.
    For more information on the xml.etree api, visit: https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
    """
    __err_msg_str = f"Only str is allowed for filename"

    if not isinstance(filename, str): raise _Xmlimportfile.xmlimportfile(__err_msg_str, f'\nFILE:"{filename}"')

    try: return __xml_etree.parse(filename).getroot()
    except FileNotFoundError as __err_msg: raise _Xmlimportfile.xmlimportfile(__err_msg, f'\nFILE:"{filename}"')
    except __xml_etree.ParseError as __err_msg: raise _Xmlimportfile.xmlimportfile(__err_msg, f'\nFILE:"{filename}"')
