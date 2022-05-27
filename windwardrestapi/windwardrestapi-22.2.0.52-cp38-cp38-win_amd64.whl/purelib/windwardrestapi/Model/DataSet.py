'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

import six
'''
A dataset that is part of a datasource. This is a member of this datasets parent datasource.
Used as part of document generation request.
'''
class DataSet(object):

    attribute_map = {
        'name': 'Name',
        'query': 'Query'
    }

    '''
    Initiaizes a new instance of the DataSet class.
    :param name: The name of this DataSet.
    :param query: The query that defines the dataset. This query is run against the parents datasource.
    '''
    def __init__(self, name=None, query=None):

        self._name = None
        self._query = None
        if name is not None:
            self.name = name
        if query is not None:
            self.query = query

    @property
    def name(self):
        """Gets the name of this DataSet.

        The dataset name. Used as the datasource name when applying to a template.

        :return: The name of this DataSet.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this DataSet.

        The dataset name. Used as the datasource name when applying to a template.

        :param name: The name of this DataSet.
        :type: str
        """

        self._name = name

    @property
    def query(self):
        """Gets the query of this DataSet.

        The query that defines the dataset. This query is run against the parent's datasource.

        :return: The query of this DataSet.
        :rtype: str
        """
        return self._query

    @query.setter
    def query(self, query):
        """Sets the query of this DataSet.

        The query that defines the dataset. This query is run against the parent's datasource.

        :param query: The query of this DataSet.
        :type: str
        """

        self._query = query

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
