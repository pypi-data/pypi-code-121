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
Datasource type.
'''
class datasouceTypeEnum():
    SQL = "sql"

    XML = "xml"

    XML2 = "xml2"

    JSON = "json"

    ODATA = "odata"

    SALESFORCE = "salesforce"

    SALESFORCEOAUTH = "salesforceoauth"

'''
A datasource to apply to a template. This can include datasets built from this datasource. Used as part of a document generation request.
'''
class Datasource(object):

    attributeMap = {
        'name': 'Name',
        'type': 'Type',
        'className': 'ClassName',
        'connectionString': 'ConnectionString',
        'schemaConnectionString': 'SchemaConnectionString',
        'data': 'Data',
        'schemaData': 'SchemaData',
        'datasets': 'Datasets'
    }

    '''
    Initializes a new instance of the Datasource class. Pass in either a data file (data) or a connection string (connectionString).
    
    :param name : The datasource name which maps to the datasource attribute in tags.
    :type str
    
    :param type: The type of this Datasource. When setting this use the datasouceTypeEnum() class in this class.
    :type str
    
    :param className : The ADO.NET connector classname. None for other types.
    :type str
    
    :param connectionString : The connection string to the datacource (if data is None)
    :type str
    
    :param schemaConnectionString : The connection string to the XSD file (XML only)
    :type str : the file path to the file as a string
    
    :param data : The JSON or XML datasource file (if connectionString is None)
    :type str : the file path to the file as a string
    
    :param datasets : The datasets associated with this datasource (if they exist)
    :type List[DataSet] : list of DataSet class objects
    '''

    def __init__(self, name=None, type=None, className=None, connectionString=None, schemaConnectionString=None, data=None, schemaData=None, datasets=None):  # noqa: E501

        self._name = None
        self._type = None
        self._className = None
        self._connectionString = None
        self._schemaConnectionString = None
        self._data = None
        self._schemaData = None
        self._datasets = []

        if name is not None:
            self.name = name
        if type is not None:
            self.type = type
        if className is not None:
            self.className = className
        if connectionString is not None:
            self.connectionString = connectionString
        if schemaConnectionString is not None:
            self.schemaConnectionString = schemaConnectionString
        if data is not None:
            dataFile = open(data, "rb")
            self.data = base64.b64encode(dataFile.read()).decode('utf-8')
        if schemaData is not None:
            schemaFile = open(data, "rb")
            self._schemaData = base64.b64encode(schemaFile.read()).decode('utf-8')
        if datasets is not None:
            self.datasets = datasets

    @property
    def name(self):
        """Gets the name of this Datasource.

        The datasource name which maps to the datasource attribute in tags.

        :return: The name of this Datasource.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Datasource.

        The datasource name which maps to the datasource attribute in tags.

        :param name: The name of this Datasource.
        :type: str
        """

        self._name = name

    @property
    def type(self):
        """Gets the type of this Datasource.

        A type of this data source.

        :return: The type of this Datasource.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Datasource.

        A type of this data source.

        :param type: The type of this Datasource.
        :type: str
        """
        allowed_values = ["sql", "xml", "xml2", "json", "odata", "salesforce", "salesforceoauth"]
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def className(self):
        """Gets the class_name of this Datasource.

        The ADO.NET connector classname. null for other types.

        :return: The class_name of this Datasource.
        :rtype: str
        """
        return self._className

    @className.setter
    def className(self, class_name):
        """Sets the class_name of this Datasource.

        The ADO.NET connector classname. null for other types.

        :param class_name: The class_name of this Datasource.
        :type: str
        """

        self._className = class_name

    @property
    def connectionString(self):
        """Gets the connection_string of this Datasource.

        The connection string to the datasource. null if passing in the Data property.  # noqa: E501

        :return: The connection_string of this Datasource.
        :rtype: str
        """
        return self._connectionString

    @connectionString.setter
    def connectionString(self, connection_string):
        """Sets the connection_string of this Datasource.

        The connection string to the datasource. null if passing in the Data property.

        :param connection_string: The connection_string of this Datasource.
        :type: str
        """

        self._connectionString = connection_string

    @property
    def schemaConnectionString(self):
        """Gets the schema_connection_string of this Datasource.

        If an XSD file is used with your XML data source use this or SchemaData. Location of external XSD file.

        :return: The schema_connection_string of this Datasource.
        :rtype: str
        """
        return self._schemaConnectionString

    @schemaConnectionString.setter
    def schemaConnectionString(self, schema_connection_string):
        """Sets the schema_connection_string of this Datasource.

        If an XSD file is used with your XML data source use this or SchemaData. Location of external XSD file.

        :param schema_connection_string: The schema_connection_string of this Datasource.
        :type: str
        """

        self._schemaConnectionString = schema_connection_string

    @property
    def data(self):
        """Gets the data of this Datasource.

        The actual data (JSON and XML only). Used when passing up the datasource as the actual data file. null if passing in the ConnectionString property.

        :return: The data of this Datasource.
        :rtype: str
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this Datasource.

        The actual data (JSON and XML only). Used when passing up the datasource as the actual data file. null if passing in the ConnectionString property.

        :param data: The data of this Datasource.
        :type: str
        """

        self._data = data

    @property
    def schemaData(self):
        """Gets the schema_data of this Datasource.

        If an XSD file is used with your XML data source use this or SchemaUri. Embed the XSD file as a Base64-encoded string.

        :return: The schema_data of this Datasource.
        :rtype: str
        """
        return self._schemaData

    @schemaData.setter
    def schemaData(self, schema_data):
        """Sets the schema_data of this Datasource.

        If an XSD file is used with your XML data source use this or SchemaUri. Embed the XSD file as a Base64-encoded string.

        :param schema_data: The schema_data of this Datasource.
        :type: str
        """

        self._schemaData = schema_data

    @property
    def datasets(self):
        """Gets the datasets of this Datasource.

        The datasets created on this datasource.

        :return: The datasets of this Datasource.
        :rtype: list[DataSet]
        """
        return self._datasets

    @datasets.setter
    def datasets(self, datasets):
        """Sets the datasets of this Datasource.

        The datasets created on this datasource.

        :param datasets: The datasets of this Datasource.
        :type: list[DataSet]
        """

        if not isinstance(datasets, list):
            self._datasets.append(datasets)
        else:
            for dSet in datasets:
                self._datasets.append(dSet)

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
