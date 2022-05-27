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
The information about an import processed generating the document.
'''
class ImportMetrics(object):


    attributeMap = {
        'type': 'Type',
        'tag': 'Tag',
        'filename': 'Filename',
        'children': 'Children'
    }
    '''
    Creates a new instance of the ImportMetrics class when generating a document.
    
    :param type : The type of the imported file
    :param tag : The full import tag that imports this file
    :param fileName : The filename of the imported file
    :param children : The child imports of the imported template
    '''
    def __init__(self, type=None, tag=None, filename=None, children=None):
        self._type = None
        self._tag = None
        self._filename = None
        self._children = None

        if type is not None:
            self.type = type
        if tag is not None:
            self.tag = tag
        if filename is not None:
            self.filename = filename
        if children is not None:
            self.children = children

    @property
    def type(self):
        """Gets the type of this ImportMetrics.

        The type of imported file.

        :return: The type of this ImportMetrics.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ImportMetrics.

        The type of imported file.

        :param type: The type of this ImportMetrics.
        :type: str
        """

        self._type = type

    @property
    def tag(self):
        """Gets the tag of this ImportMetrics.

        The full import tag that imports this file.

        :return: The tag of this ImportMetrics.
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this ImportMetrics.

        The full import tag that imports this file.

        :param tag: The tag of this ImportMetrics.
        :type: str
        """

        self._tag = tag

    @property
    def filename(self):
        """Gets the filename of this ImportMetrics.

        The filename of the file imported.

        :return: The filename of this ImportMetrics.
        :rtype: str
        """
        return self._filename

    @filename.setter
    def filename(self, filename):
        """Sets the filename of this ImportMetrics.

        The filename of the file imported.

        :param filename: The filename of this ImportMetrics.
        :type: str
        """

        self._filename = filename

    @property
    def children(self):
        """Gets the children of this ImportMetrics.

        The child imports of this imported template.

        :return: The children of this ImportMetrics.
        :rtype: list[ImportMetrics]
        """
        return self._children

    @children.setter
    def children(self, children):
        """Sets the children of this ImportMetrics.

        The child imports of this imported template.

        :param children: The children of this ImportMetrics.
        :type: list[ImportMetrics]
        """

        self._children = children

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
