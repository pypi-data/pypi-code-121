'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

import six

class Issue(object):

    attributeMap = {
        'message': 'Message',
        'isError': 'IsError',
        'isWarning': 'IsWarning',
        'issueType': 'IssueType',
        'tag': 'Tag'
    }

    def __init__(self, message=None, isError=None, isWarning=None, issueType=None, tag=None):

        self._message = None
        self._isError = None
        self._isWarning = None
        self._issueType = None
        self._tag = None

        if message is not None:
            self.message = message
        if isError is not None:
            self.isError = isError
        if isWarning is not None:
            self.isWarning = isWarning
        if issueType is not None:
            self.issueType = issueType
        if tag is not None:
            self.tag = tag

    @property
    def message(self):
        """Gets the message of this Issue.

        A textual description of this issue.

        :return: The message of this Issue.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this Issue.

        A textual description of this issue.

        :param message: The message of this Issue.
        :type: str
        """

        self._message = message

    @property
    def isError(self):
        """Gets the is_error of this Issue.

        True if this issue is an error.

        :return: The is_error of this Issue.
        :rtype: bool
        """
        return self._isError

    @isError.setter
    def isError(self, is_error):
        """Sets the is_error of this Issue.

        True if this issue is an error.

        :param is_error: The is_error of this Issue.
        :type: bool
        """

        self._isError = is_error

    @property
    def isWarning(self):
        """Gets the is_warning of this Issue.

        True if this issue is a warning.

        :return: The is_warning of this Issue.
        :rtype: bool
        """
        return self._isWarning

    @isWarning.setter
    def isWarning(self, is_warning):
        """Sets the is_warning of this Issue.

        True if this issue is a warning.

        :param is_warning: The is_warning of this Issue.
        :type: bool
        """

        self._isWarning = is_warning

    @property
    def issueType(self):
        """Gets the issue_type of this Issue.

        The .Net engine Issue.IssueType.

        :return: The issue_type of this Issue.
        :rtype: str
        """
        return self._issueType

    @issueType.setter
    def issueType(self, issue_type):
        """Sets the issue_type of this Issue.

        The .Net engine Issue.IssueType.

        :param issue_type: The issue_type of this Issue.
        :type: str
        """
        allowed_values = ["Type", "Formatting", "Select", "NodeDoesNotExist", "NodeNull", "Verify"]
        if issue_type not in allowed_values:
            raise ValueError(
                "Invalid value for `issue_type` ({0}), must be one of {1}"
                    .format(issue_type, allowed_values)
            )

        self._issueType = issue_type

    @property
    def tag(self):
        """Gets the tag of this Issue.

        The tag that led to this issue. This is the tag from the source template.

        :return: The tag of this Issue.
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this Issue.

        The tag that led to this issue. This is the tag from the source template.

        :param tag: The tag of this Issue.
        :type: str
        """

        self._tag = tag

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
