'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

import six


class ServiceError(object):

    attributeMap = {
        'message': 'Message',
        'type': 'Type',
        'inner_error': 'InnerError'
    }

    def __init__(self, message=None, type=None, innerError=None):

        self._message = None
        self._type = None
        self._innerError = None

        if message is not None:
            self.message = message
        if type is not None:
            self.type = type
        if innerError is not None:
            self.innerError = innerError

    @property
    def message(self):
        """Gets the message of this ServiceError.

        The exception message.

        :return: The message of this ServiceError.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this ServiceError.

        The exception message.

        :param message: The message of this ServiceError.
        :type: str
        """

        self._message = message

    @property
    def type(self):
        """Gets the type of this ServiceError.

        The exception type.

        :return: The type of this ServiceError.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ServiceError.

        The exception type.

        :param type: The type of this ServiceError.
        :type: str
        """

        self._type = type

    @property
    def innerError(self):
        """Gets the inner_error of this ServiceError.


        :return: The inner_error of this ServiceError.
        :rtype: ServiceError
        """
        return self._innerError

    @innerError.setter
    def innerError(self, inner_error):
        """Sets the inner_error of this ServiceError.


        :param inner_error: The inner_error of this ServiceError.
        :type: ServiceError
        """

        self._innerError = inner_error

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