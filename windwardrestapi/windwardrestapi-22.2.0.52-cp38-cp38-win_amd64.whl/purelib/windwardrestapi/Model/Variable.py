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
A var in a template that must be define before the template is processed
'''
class Variable(object):

    attributeMap = {
        'name': 'Name',
        'description': 'Description',
        'type': 'Type',
        'required': 'Required',
        'allowAll': 'AllowAll',
        'allowList': 'AllowList',
        'allowFilter': 'AllowFilter',
        'allowSort': 'AllowSort',
        'autoMetadata': 'AutoMetadata',
        'defaultValues': 'DefaultValues',
        'allowedValues': 'AllowedValues',
        'datasource': 'Datasource',
        'calOffset': 'CalOffset',
        'select': 'Select',
        'selectFormat': 'SelectFormat'
    }

    '''
    Initializes a new instance of the Template class

    :param  name : The name of the variable
    :type str

    :param description : The default value of the variable, None if undefined
    :type str

    :param type : The type of the variable given in Value
    :type str 

    :param required : True if the variable is required to process the template
    :type bool

    :param allowAll : Can return all the values for this select variable
    :type bool

    :param allowList : Can return a list of  values for this select variable
    :type bool

    :param allowFilter : Can set a filter for values for this select variable
    :type bool

    :param allowSort : Can sort values for this variable
    :type bool

    :param autoMetadata : If this is an auto-select, this is the metadata for the select. For SQL this is [dbo.]table.column
    using the raw values (no surrounding spaces) and for XML it is the full XPath to that node.
    :type str

    :param defaultValues :  The default values for this var. Can be length 0 (which means no default).
    :type List[VariableValue]

    :param allowedValues : The allowed values for this var. Can be length 0 (which means anything is allowed OR the list was too long).
    :type List[VariableValue]

    :param datasource : The name of the datasource for the select
    :type str

    :param callOffset : The date default could be set to a calander offset
    :type str

    :param select : The Select for this var if a select var. None if not a select var
    :type str

    :param selectFormat : The Select format for this var if a select var. None if not a select var.
    :type str
    '''
    def __init__(self, name=None, description=None, type=None, required=None, allowAll=None, allowList=None,
                 allowFilter=None, allowSort=None, autoMetadata=None, defaultValues=None, allowedValues=None,
                 datasource=None, calOffset=None, select=None, selectFormat=None):

        self._name = None
        self._description = None
        self._type = None
        self._required = False
        self._allowAll = False
        self._allowList = False
        self._allowFilter = False
        self._allowSort = False
        self._autoMetadata = None
        self._defaultValues = []
        self._allowedValues = []
        self._datasource = None
        self._calOffset = None
        self._select = None
        self._selectFormat = None

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if type is not None:
            self.type = type
        if required is not None:
            self.required = required
        if allowAll is not None:
            self.allowAll = allowAll
        if allowList is not None:
            self.allowList = allowList
        if allowFilter is not None:
            self.allowFilter = allowFilter
        if allowSort is not None:
            self.allowSort = allowSort
        if autoMetadata is not None:
            self.autoMetadata = autoMetadata
        if defaultValues is not None:
            self.defaultValues = defaultValues
        if allowedValues is not None:
            self.allowedValues = allowedValues
        if datasource is not None:
            self.datasource = datasource
        if calOffset is not None:
            self.calOffset = calOffset
        if select is not None:
            self.select = select
        if selectFormat is not None:
            self.selectFormat = selectFormat

    @property
    def name(self):
        """Gets the name of this Variable.

        The name of the variable.

        :return: The name of this Variable.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Variable.

        The name of the variable.

        :param name: The name of this Variable.
        :type: str
        """

        self._name = name

    @property
    def description(self):
        """Gets the description of this Variable.

        The default value of the variable, null if undefined.

        :return: The description of this Variable.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Variable.

        The default value of the variable, null if undefined.

        :param description: The description of this Variable.
        :type: str
        """

        self._description = description

    @property
    def type(self):
        """Gets the type of this Variable.

        The type of variable given in Value.

        :return: The type of this Variable.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Variable.

        The type of variable given in Value.

        :param type: The type of this Variable.
        :type: str
        """

        self._type = type

    @property
    def required(self):
        """Gets the required of this Variable.

        true if the variable is required for the template to generate.

        :return: The required of this Variable.
        :rtype: bool
        """
        return self._required

    @required.setter
    def required(self, required):
        """Sets the required of this Variable.

        true if the variable is required for the template to generate.

        :param required: The required of this Variable.
        :type: bool
        """

        self._required = required

    @property
    def allowAll(self):
        """Gets the allow_all of this Variable.

        Can return all values for this select variable.

        :return: The allow_all of this Variable.
        :rtype: bool
        """
        return self._allowAll

    @allowAll.setter
    def allowAll(self, allow_all):
        """Sets the allow_all of this Variable.

        Can return all values for this select variable.

        :param allow_all: The allow_all of this Variable.
        :type: bool
        """

        self._allowAll = allow_all

    @property
    def allowList(self):
        """Gets the allow_list of this Variable.

        Can return a list of values for this select variable.

        :return: The allow_list of this Variable.
        :rtype: bool
        """
        return self._allowList

    @allowList.setter
    def allowList(self, allow_list):
        """Sets the allow_list of this Variable.

        Can return a list of values for this select variable.

        :param allow_list: The allow_list of this Variable.
        :type: bool
        """

        self._allow_list = allow_list

    @property
    def allowFilter(self):
        """Gets the allow_filter of this Variable.

        Can set a filter for values for this select variable.

        :return: The allow_filter of this Variable.
        :rtype: bool
        """
        return self._allowFilter

    @allowFilter.setter
    def allowFilter(self, allow_filter):
        """Sets the allow_filter of this Variable.

        Can set a filter for values for this select variable.

        :param allow_filter: The allow_filter of this Variable.
        :type: bool
        """

        self._allowFilter = allow_filter

    @property
    def allowSort(self):
        """Gets the allow_sort of this Variable.

        Can sort values for this select variable.

        :return: The allow_sort of this Variable.
        :rtype: bool
        """
        return self._allowSort

    @allowSort.setter
    def allowSort(self, allow_sort):
        """Sets the allow_sort of this Variable.

        Can sort values for this select variable.

        :param allow_sort: The allow_sort of this Variable.
        :type: bool
        """

        self._allowSort = allow_sort

    @property
    def autoMetadata(self):
        """Gets the auto_metadata of this Variable.

        If this is an auto-select, this is the metadata for the select. For SQL this is [dbo.]table.column using the raw values (no surrounding spaces) and for XML it is the full XPath to that node.

        :return: The auto_metadata of this Variable.
        :rtype: str
        """
        return self._autoMetadata

    @autoMetadata.setter
    def autoMetadata(self, auto_metadata):
        """Sets the auto_metadata of this Variable.

        If this is an auto-select, this is the metadata for the select. For SQL this is [dbo.]table.column using the raw values (no surrounding spaces) and for XML it is the full XPath to that node.

        :param auto_metadata: The auto_metadata of this Variable.
        :type: str
        """

        self._autoMetadata = auto_metadata

    @property
    def defaultValues(self):
        """Gets the default_values of this Variable.

        The default values for this var. Can be length 0 (which means no default).

        :return: The default_values of this Variable.
        :rtype: list[VariableValue]
        """
        return self._defaultValues

    @defaultValues.setter
    def defaultValues(self, default_values):
        """Sets the default_values of this Variable.

        The default values for this var. Can be length 0 (which means no default).

        :param default_values: The default_values of this Variable.
        :type: list[VariableValue]
        """

        self._defaultValues = default_values

    @property
    def allowedValues(self):
        """Gets the allowed_values of this Variable.

        The allowed values for this var. Can be length 0 (which means anything is allowed OR the list was too long).

        :return: The allowed_values of this Variable.
        :rtype: list[VariableValue]
        """
        return self._allowedValues

    @allowedValues.setter
    def allowedValues(self, allowed_values):
        """Sets the allowed_values of this Variable.

        The allowed values for this var. Can be length 0 (which means anything is allowed OR the list was too long).

        :param allowed_values: The allowed_values of this Variable.
        :type: list[VariableValue]
        """

        self._allowedValues = allowed_values

    @property
    def datasource(self):
        """Gets the datasource of this Variable.

        The name of the datasource for the select.

        :return: The datasource of this Variable.
        :rtype: str
        """
        return self._datasource

    @datasource.setter
    def datasource(self, datasource):
        """Sets the datasource of this Variable.

        The name of the datasource for the select.

        :param datasource: The datasource of this Variable.
        :type: str
        """

        self._datasource = datasource

    @property
    def calOffset(self):
        """Gets the cal_offset of this Variable.

        The date default value can be set to a calendar offset.

        :return: The cal_offset of this Variable.
        :rtype: str
        """
        return self._calOffset

    @calOffset.setter
    def calOffset(self, cal_offset):
        """Sets the cal_offset of this Variable.

        The date default value can be set to a calendar offset.

        :param cal_offset: The cal_offset of this Variable.
        :type: str
        """

        self._calOffset = cal_offset

    @property
    def select(self):
        """Gets the select of this Variable.

        The Select for this var if a select var. null if not a select var.

        :return: The select of this Variable.
        :rtype: str
        """
        return self._select

    @select.setter
    def select(self, select):
        """Sets the select of this Variable.

        The Select for this var if a select var. null if not a select var.

        :param select: The select of this Variable.
        :type: str
        """

        self._select = select

    @property
    def selectFormat(self):
        """Gets the select_format of this Variable.

        The Select format for this var if a select var. null if not a select var.

        :return: The select_format of this Variable.
        :rtype: str
        """
        return self._selectFormat

    @selectFormat.setter
    def selectFormat(self, select_format):
        """Sets the select_format of this Variable.

        The Select format for this var if a select var. null if not a select var.

        :param select_format: The select_format of this Variable.
        :type: str
        """

        self._selectFormat = select_format

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
