'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

import six
from windwardrestapi.Model import Entry

'''
A datasource to apply to a template. This can include datasets built from this datasource. Used as part of a document generation request.
'''
class DataSetProfile(object):

    attribute_map = {
        'name': 'Name',
        'select': 'Select',
        'properties': 'Properties'
    }

    def __init__(self, name=None, select=None, properties=None):

        self._name = None
        self._select = None
        self._properties = []

        if name is not None:
            self.name = name
        if select is not None:
            self.select = select
        if properties is not None:
            self.properties = properties

    @property
    def name(self):
        """Gets the name of this DataSetProfile.

        The name used to reference this dataset.

        :return: The name of this DataSetProfile.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this DataSetProfile.

        The name used to reference this dataset.

        :param name: The name of this DataSetProfile.
        :type: str
        """

        self._name = name

    @property
    def select(self):
        """Gets the select of this DataSetProfile.

        The select of this dataset.

        :return: The select of this DataSetProfile.
        :rtype: str
        """
        return self._select

    @select.setter
    def select(self, select):
        """Sets the select of this DataSetProfile.

        The select of this dataset.  # noqa: E501

        :param select: The select of this DataSetProfile.
        :type: str
        """

        self._select = select

    @property
    def properties(self):
        """Gets the properties of this DataSetProfile.

        All information defining this dataset as a collection of properties.

        :return: The properties of this DataSetProfile.
        :rtype: list[Entry]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this DataSetProfile.

        All information defining this dataset as a collection of properties.

        :param properties: The properties of this DataSetProfile.
        :type: list[Entry]
        """
        for prop in properties:
            for k, v in prop.items():
                key = k
                value = v
                print("Key: ", key, ", Value: ", value, "\n")
                self._properties.append(Entry.Entry(key=key, value=value))

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
