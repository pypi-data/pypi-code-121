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
A SalesforceOAuth datasource to to apply to a template. This can include datasets built from this datasource. Used as part of the document
generation request.
'''
class SalesforceOAuthDataSource(Datasource.Datasource):
    '''
    Initialize a new instance of the DataSource class and set the type to SalesforceOAuth

    :param name : The datasource name that maps to the datasource attribute in tags
    :type str

    :param connectionString : The connection string to the SalesforceOAuth data
    :type str
    '''
    def __init__(self, name, connectionString=None):
        super().__init__(name=name, connectionString=connectionString, type= Datasource.datasouceTypeEnum.SALESFORCEOAUTH)