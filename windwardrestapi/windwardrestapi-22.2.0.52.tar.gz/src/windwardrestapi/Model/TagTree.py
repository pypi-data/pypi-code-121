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
The generated tag tree we are sending back to the client. Also used as a pending tagtree job where only the Guid and the
Tag properties are set.
'''
class TagTree(object):

    attributeMap = {
        'guid': 'Guid',
        'tag': 'Tag',
        'xml': 'Xml'
    }
    '''
    Initializes a new instance of the TagTree class.
    
    :param guid : The guid of the asyn job
    :type str
    
    :param Tag : The tag set for the template this tagtree is produced from
    :type str
    
    :param xml : The tag tree which is an XML doucment
    :type base64 str
    '''
    def __init__(self, response):

        self._guid = None
        self._tag = None
        self._xml = None

        if "Guid" in response:
            self.guid = response["Guid"]
        if "Tag" in response:
            self.tag = response["Tag"]
        if "Xml" in response:
            self.xml = response["Xml"]

    @property
    def guid(self):
        """Gets the guid of this TagTree.

        The guid of this async job.

        :return: The guid of this TagTree.
        :rtype: str
        """
        return self._guid

    @guid.setter
    def guid(self, guid):
        """Sets the guid of this TagTree.

        The guid of this async job.

        :param guid: The guid of this TagTree.
        :type: str
        """

        self._guid = guid

    @property
    def tag(self):
        """Gets the tag of this TagTree.

        Anything you want. This is set in the Template and passed in to the repository & job handlers and is set in the final generated TagTree object. The RESTful engine ignores this setting, it is for the caller's use.

        :return: The tag of this TagTree.
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this TagTree.

        Anything you want. This is set in the Template and passed in to the repository & job handlers and is set in the final generated TagTree object. The RESTful engine ignores this setting, it is for the caller's use.

        :param tag: The tag of this TagTree.
        :type: str
        """

        self._tag = tag

    @property
    def xml(self):
        """Gets the xml of this TagTree.

        The tag tree which is an XML document.

        :return: The xml of this TagTree.
        :rtype: str
        """
        return self._xml

    @xml.setter
    def xml(self, xml):
        """Sets the xml of this TagTree.

        The tag tree which is an XML document.

        :param xml: The xml of this TagTree.
        :type: str
        """

        self._xml = xml

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
