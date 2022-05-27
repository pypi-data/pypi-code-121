'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

from windwardrestapi.Model import Datasource
'''
A Xml1 datasource to to apply to a template. This can include datasets built from this datasource. Used as part of the document
generation request.
'''
class Xml_10DataSource(Datasource.Datasource):
    '''
    Initialize a new instance of the DataSource class and set the type to XML10

    :param name : The datasource name that maps to the datasource attribute in tags
    :type str

    :param connectionString : The connection string to the XML1 data (only use if data is None)
    :type str

    :param data : The file path to the XML1 data file (only use if connectionString is None)
    :type str : the file path to the XML1 data file as a string

    :param schemaConnectionString : The connection string to the XSD file. None if no schema
    :type str
    '''

    def __init__(self, name, connectionString=None, data=None, schemaConnectionString=None, schemaData=None):
        super().__init__(name=name, connectionString=connectionString, data=data,
                         schemaConnectionString=schemaConnectionString, schemaData=schemaData,
                         type=Datasource.datasouceTypeEnum.XML)