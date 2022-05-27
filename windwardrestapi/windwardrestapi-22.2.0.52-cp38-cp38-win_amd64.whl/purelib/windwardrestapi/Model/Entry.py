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
A key value pair used in the data returned from the TagTree and Metrics for properties.
'''
class Entry(object):

    attributeMap = {
        'key': 'Key',
        'value': 'Value'
    }
    '''
    Creates a new instance of the Entry class object.
    
    :param key : The key (name) of the property
    :param value : The value of the property
    '''
    def __init__(self, key=None, value=None):

        self._key = None
        self._value = None

        if key is not None:
            self.key = key
        if value is not None:
            self.value = value

    @property
    def key(self):
        """Gets the key of this Entry.

        The key (name) of the property.

        :return: The key of this Entry.
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this Entry.

        The key (name) of the property.

        :param key: The key of this Entry.
        :type: str
        """

        self._key = key

    @property
    def value(self):
        """Gets the value of this Entry.

        The value of the property.

        :return: The value of this Entry.
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this Entry.

        The value of the property.

        :param value: The value of this Entry.
        :type: str
        """

        self._value = value

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
