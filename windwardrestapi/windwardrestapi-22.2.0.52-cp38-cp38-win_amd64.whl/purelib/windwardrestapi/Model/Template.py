'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

import six
import base64

'''
Generate report in provided format
'''
class outputFormatEnum():
    PDF = "pdf"

    DOCX = "docx"

    XLSX = "xlsx"

    PPTX = "pptx"

    TXT = "txt"

    HTML = "html"

    TXT = "txt"

    PRN = "prn"

    CSV = "csv"

    RTF = "rtf"

    JPG = "jpg"

    PNG = "png"


class Template(object):


    attributeMap = {
        'callback': 'Callback',
        'outputFormat': 'OutputFormat',
        'data': 'Data',
        'connectionString': 'ConnectionString',
        'format': 'Format',
        'properties': 'Properties',
        'parameters': 'Parameters',
        'datasources': 'Datasources',
        'tag': 'Tag',
        'trackImports': 'TrackImports',
        'trackErrors': 'TrackErrors',
        'mainPrinter': 'MainPrinter',
        'firstPagePrinter': 'FirstPagePrinter',
        'printerJobName': 'PrinterJobName',
        'printCopies': 'PrintCopies',
        'printDuplex': 'PrintDuplex'
    }

    '''
    Initializes a new instance of the Template class
    
    :param callback : If set, this url will be called with a POST when a job completes. If the text "{guid}" is in the url, that text will
    be replaced with the Guid for the callback.
    :type str
    
    :param outputFormat : The desired output file type (set using the Template.outputFormatEnum())
    :type str
    
    :param data : The file path for your template (the client will encode to base64) (only use if connectionString is None)
    :type str : string representation of the file path
    
    :param connectionString : The connection string to your template file (only use if data is None)
    :type str
    
    :param format : The format of the template to be processed (if left empty it will auto populate)
    :type str
    
    :param properties : Windward properties for this report. These override any properties set in the configuration file on the server side.
    :type List[Property] : A list of Property objects
    
    :param parameters : A set of input parameters for this report. The parameters are global and shared among all data sources.
    :type List[Parameter] : A list of Property objects
    
    :param datasources : The datasources to apply to the template. The datasources are applied simultaneously.
    :type List[Datasource] : A list of Datasource objects
    
    :param tag : A tag you want to assign to the template. 
    This is passed in to the repository job handlers and is set in the final generated Report object
    :type str
    
    :param trackImports : Return all imports with the generated document
    :type bool
    
    :param trackErrors : Enable or disable the error handling and verify functionality.
    :type bool
    
    :param mainPrinter : If you are using printer output use to specify main printer. Printer must be recognized by Network
    :type str
    
    :param firstPagePrinter : Set first page printer if main printer is already set
    :type str
    
    :param printerJobName : Assign the print job a name
    :type str
    
    :param printCopies : Set number of copies the print job should print
    :type str
    
    :param printDuplex : Selects the printers duplex mode
    :type str
    '''
    def __init__(self, callback=None, outputFormat=None, data=None, connectionString=None, format=None, properties=None,
                 parameters=None, datasources=None, tag=None, trackImports=None, trackErrors=None, mainPrinter=None,
                 firstPagePrinter=None, printerJobName=None, printCopies=None, printDuplex=None):
        self._callback = None
        self._outputFormat = None
        self._data = None
        self._connectionString = None
        self._format = None
        self._properties = []
        self._parameters = []
        self._datasources = []
        self._tag = None
        self._trackImports = False
        self._trackErrors = 0
        self._mainPrinter = None
        self._firstPagePrinter = None
        self._printerJobName = None
        self._printCopies = 0
        self._printDuplex = None

        if callback is not None:
            self.callback = callback
        if outputFormat is not None:
            self.outputFormat = outputFormat
        if data is not None:
            dataFile = open(data, "rb")
            self.data = base64.b64encode(dataFile.read()).decode('utf-8')
        if connectionString is not None:
            self.connectionString = connectionString
        if format is not None:
            self.format = format
        if properties is not None:
            self.properties = properties
        if parameters is not None:
            self.parameters = parameters
        if datasources is not None:
            self.datasources = datasources
        if tag is not None:
            self.tag = tag
        if trackImports is not None:
            self.trackImports = trackImports
        if trackErrors is not None:
            self.trackErrors = trackErrors
        if mainPrinter is not None:
            self.mainPrinter = mainPrinter
        if firstPagePrinter is not None:
            self._firstPagePrinter = firstPagePrinter
        if printerJobName is not None:
            self._printerJobName = printerJobName
        if printCopies is not None:
            self._printCopies = printCopies
        if printDuplex is not None:
            self._printDuplex = printDuplex
    '''
    * Generate the document in the provided format.
    '''


    @property
    def callback(self):
        """Gets the callback of this Template.

        If set, this url will be called with a POST when a job completes. If the text \"{guid}\" is in the url, that text will be replaced with the Guid for the callback.  # noqa: E501

        :return: The callback of this Template.
        :rtype: str
        """
        return self._callback

    @callback.setter
    def callback(self, callback):
        """Sets the callback of this Template.

        If set, this url will be called with a POST when a job completes. If the text \"{guid}\" is in the url, that text will be replaced with the Guid for the callback.

        :param callback: The callback of this Template.
        :type: str
        """

        self._callback = callback

    @property
    def outputFormat(self):
        """Gets the output_format of this Template.

        Generate the document in the provided format.

        :return: The output_format of this Template.
        :rtype: str
        """
        return self._outputFormat

    @outputFormat.setter
    def outputFormat(self, output_format):
        """Sets the output_format of this Template.

        Generate the document in the provided format.

        :param output_format: The output_format of this Template.
        :type: str
        """
        allowed_values = ["pdf", "docx", "xlsx", "pptx", "txt", "html", "prn", "csv", "rtf", "jpg", "png", "svg", "eps", "bmp",
                          "gif"]
        if output_format not in allowed_values:
            raise ValueError(
                "Invalid value for `output_format` ({0}), must be one of {1}"
                    .format(output_format, allowed_values)
            )

        self._outputFormat = output_format

    @property
    def data(self):
        """Gets the data of this Template.

        The source of the template- embedded or external. Embed template as a Base64-encoded string.

        :return: The data of this Template.
        :rtype: str
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this Template.

        The source of the template- embedded or external. Embed template as a Base64-encoded string.

        :param data: The data of this Template.
        :type: str
        """

        self._data = data

    @property
    def connectionString(self):
        """Gets the uri of this Template.

        Set this to provide the template as a connection string of the template's location.

        :return: The uri of this Template.
        :rtype: str
        """
        return self._connectionString

    @connectionString.setter
    def connectionString(self, uri):
        """Sets the uri of this Template.

        Set this to provide the template as a connection string of the template's location.

        :param uri: The uri of this Template.
        :type: str
        """

        self._connectionString = uri

    @property
    def format(self):
        """Gets the format of this Template.

        Format of the template. Auto-determined if not provided.

        :return: The format of this Template.
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this Template.

        Format of the template. Auto-determined if not provided.

        :param format: The format of this Template.
        :type: str
        """
        allowed_values = ["docx", "html", "xlsx", "pptx"]
        if format not in allowed_values:
            raise ValueError(
                "Invalid value for `format` ({0}), must be one of {1}"
                    .format(format, allowed_values)
            )

        self._format = format

    @property
    def properties(self):
        """Gets the properties of this Template.

        Windward properties for this document. These override any properties set in the configuration file on the server side.  # noqa: E501

        :return: The properties of this Template.
        :rtype: list[Property]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this Template.

        Windward properties for this document. These override any properties set in the configuration file on the server side.

        :param properties: The properties of this Template.
        :type: list[Property]
        """

        if not isinstance(properties, list):
            self._properties.append(properties)
        else:
            for prop in properties:
                self._properties.append(prop)

    @property
    def parameters(self):
        """Gets the parameters of this Template.

        A set of input parameters for this document. The parameters are global and shared among all data sources.

        :return: The parameters of this Template.
        :rtype: list[Parameter]
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this Template.

        A set of input parameters for this document. The parameters are global and shared among all data sources.

        :param parameters: The parameters of this Template.
        :type: list[Parameter]
        """

        if not isinstance(parameters, list):
            self._parameters.append(parameters)
        else:
            for param in parameters:
                self._parameters.append(param)

    @property
    def datasources(self):
        """Gets the datasources of this Template.

        The datasources to apply to the template. The datasources are applied simultaneously.

        :return: The datasources of this Template.
        :rtype: list[Datasource]
        """
        return self._datasources

    @datasources.setter
    def datasources(self, datasources):
        """Sets the datasources of this Template.

        The datasources to apply to the template. The datasources are applied simultaneously.

        :param datasources: The datasources of this Template.
        :type: list[Datasource]
        """
        if not isinstance(datasources, list):
            self._datasources.append(datasources)
        else:
            for ds in datasources:
                self._datasources.append(ds)

    @property
    def tag(self):
        """Gets the tag of this Template.

        Anything you want. This is passed in to the repository & job handlers and is set in the final generated document object. The RESTful engine ignores this setting, it is for the caller's use.

        :return: The tag of this Template.
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this Template.

        Anything you want. This is passed in to the repository & job handlers and is set in the final generated document object. The RESTful engine ignores this setting, it is for the caller's use.

        :param tag: The tag of this Template.
        :type: str
        """

        self._tag = tag

    @property
    def trackImports(self):
        """Gets the track_imports of this Template.

        Return all imports with the generated document.

        :return: The track_imports of this Template.
        :rtype: bool
        """
        return self._trackImports

    @trackImports.setter
    def trackImports(self, track_imports):
        """Sets the track_imports of this Template.

        Return all imports with the generated document.

        :param track_imports: The track_imports of this Template.
        :type: bool
        """

        self._trackImports = track_imports

    @property
    def trackErrors(self):
        """Gets the track_errors of this Template.

        Enable or disable the error handling and verify functionality.

        :return: The track_errors of this Template.
        :rtype: int
        """
        return self._trackErrors

    @trackErrors.setter
    def trackErrors(self, track_errors):
        """Sets the track_errors of this Template.

        Enable or disable the error handling and verify functionality.

        :param track_errors: The track_errors of this Template.
        :type: int
        """

        self._trackErrors = track_errors

    @property
    def mainPrinter(self):
        """Gets the main_printer of this Template.

        If you are using printer output use to specify main printer. Printer must be recognized by Network

        :return: The main_printer of this Template.
        :rtype: str
        """
        return self._mainPrinter

    @mainPrinter.setter
    def mainPrinter(self, main_printer):
        """Sets the main_printer of this Template.

        If you are using printer output use to specify main printer. Printer must be recognized by Network  # noqa: E501

        :param main_printer: The main_printer of this Template.  # noqa: E501
        :type: str
        """

        self._mainPrinter = main_printer

    @property
    def firstPagePrinter(self):
        """Gets the first_page_printer of this Template.

        Set first page printer if main printer is already set

        :return: The first_page_printer of this Template.
        :rtype: str
        """
        return self._firstPagePrinter

    @firstPagePrinter.setter
    def firstPagePrinter(self, first_page_printer):
        """Sets the first_page_printer of this Template.

        Set first page printer if main printer is already set

        :param first_page_printer: The first_page_printer of this Template.
        :type: str
        """

        self._firstPagePrinter = first_page_printer

    @property
    def printerJobName(self):
        """Gets the printer_job_name of this Template.

        Assign print job name  # noqa: E501

        :return: The printer_job_name of this Template.
        :rtype: str
        """
        return self._printerJobName

    @printerJobName.setter
    def printerJobName(self, printer_job_name):
        """Sets the printer_job_name of this Template.

        Assign print job name

        :param printer_job_name: The printer_job_name of this Template.
        :type: str
        """

        self._printerJobName = printer_job_name

    @property
    def printCopies(self):
        """Gets the print_copies of this Template.

        Set number of copies to print

        :return: The print_copies of this Template.
        :rtype: int
        """
        return self._printCopies

    @printCopies.setter
    def printCopies(self, print_copies):
        """Sets the print_copies of this Template.

        Set number of copies to print

        :param print_copies: The print_copies of this Template.
        :type: int
        """

        self._printCopies = print_copies

    @property
    def printDuplex(self):
        """Gets the print_duplex of this Template.

        Selects the printer duplex mode.  Only if supported by the printer.

        :return: The print_duplex of this Template.
        :rtype: str
        """
        return self._printDuplex

    @printDuplex.setter
    def printDuplex(self, print_duplex):
        """Sets the print_duplex of this Template.

        Selects the printer duplex mode.  Only if supported by the printer.

        :param print_duplex: The print_duplex of this Template.
        :type: str
        """

        self._printDuplex = print_duplex

    def toDict(self):
        responseDict = {}
        for key, value in six.iteritems(self.attributeMap):
            tempVal = getattr(self, key)
            if tempVal is None:
                pass
            elif isinstance(tempVal, (str, int, dict)):
                responseDict.update({value: tempVal})
            elif isinstance(tempVal, list):

                responseDict.update({value: []})

                for item in tempVal:
                    if isinstance(item, (str, int, dict)):
                        responseDict.update({value: tempVal})
                    else:

                        responseDict[value].append(item.toDict())
            else:
                responseDict.update({value: tempVal.toDict()})
        return responseDict


