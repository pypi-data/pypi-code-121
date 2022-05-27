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
A property set at the report level
'''
class Property(object):
    attribute_map = {
        'name': 'Name',
        'value': 'Value'
    }
    '''
    Initializes a new instance of the Property class
    
    :param name : The name of this property
    :type str
    
    :param value : The value of this property
    :type str
    '''
    def __init__(self, name=None, value=None):

        self._name = None
        self._value = None
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value

    @property
    def name(self):
        """Gets the name of this Property.

        The name of the property.

        :return: The name of this Property.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Property.

        The name of the property.

        :param name: The name of this Property.
        :type: str
        """

        self._name = name

    @property
    def value(self):
        """Gets the value of this Property.

        The value of the property.

        :return: The value of this Property.
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this Property.

        The value of the property.

        :param value: The value of this Property.
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

