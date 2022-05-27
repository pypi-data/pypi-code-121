'''
Copyright (c) 2020 by Windward Studios, Inc. All rights reserved.
This software is the confidential and proprietary information of
Windward Studios ("Confidential Information").  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Windward Studios, Inc.
'''

import six

from windwardrestapi.Model import ParameterValue, VariableValue, Variable, DataSourceProfile

'''
The metrics from a template. This is the metadata stored in the template and within the tags.  Also used as a pending metrics job
where just the Guid and Tag properties are set.
'''
class Metrics(object):

    attributeMap = {
        'guid': 'Guid',
        'tag': 'Tag',
        'templateType': 'TemplateType',
        'datasources': 'Datasources',
        'vars': 'Vars',
        'variables': 'Variables',
        'datasourceProfiles': 'DatasourceProfiles',
        'autotagVersion': 'AutotagVersion'
    }

    def __init__(self, response):

        self._guid = None
        self._tag = None
        self._template_type = None
        self._datasources = None
        self._vars = None
        self._variables = []
        self._datasourceProfiles = []
        self._autotagVersion = None
        if "Guid" in response:
            self.guid = response["Guid"]
        if "Tag" in response:
            self.tag = response["Tag"]
        if "TemplateType" in response and response["TemplateType"] is not None:
            self.templateType = response["TemplateType"]
        if "Datasources" in response:
            self.datasources = response["Datasources"]
        if "Vars" in response:
            self.vars = response["Vars"]
        if "Variables" in response  and response["Variables"] is not None:
            self.variables = response["Variables"]
        if "DatasourceProfiles" in response  and response["DatasourceProfiles"] is not None:
            self.datasourceProfiles = response["DatasourceProfiles"]
        if "AutoTagVersion" in response:
            self.autotagVersion = response["AutoTagVersion"]

    @property
    def guid(self):
        """Gets the guid of this Metrics.

        The guid of this async job.

        :return: The guid of this Metrics.
        :rtype: str
        """
        return self._guid

    @guid.setter
    def guid(self, guid):
        """Sets the guid of this Metrics.

        The guid of this async job.

        :param guid: The guid of this Metrics.
        :type: str
        """

        self._guid = guid

    @property
    def tag(self):
        """Gets the tag of this Metrics.

        Anything you want. This is passed from the Template to the repository & job handlers and is set in this final generated Metrics object. The RESTful engine ignores this setting, it is for the caller's use.

        :return: The tag of this Metrics.
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this Metrics.

        Anything you want. This is passed from the Template to the repository & job handlers and is set in this final generated Metrics object. The RESTful engine ignores this setting, it is for the caller's use.

        :param tag: The tag of this Metrics.
        :type: str
        """

        self._tag = tag

    @property
    def templateType(self):
        """Gets the template_type of this Metrics.

        The format of the template as a .Net Engine Report.TEMPLATE_TYPE.

        :return: The template_type of this Metrics.
        :rtype: str
        """
        return self._templateType

    @templateType.setter
    def templateType(self, template_type):
        """Sets the template_type of this Metrics.

        The format of the template as a .Net Engine Report.TEMPLATE_TYPE.

        :param template_type: The template_type of this Metrics.
        :type: str
        """
        allowed_values = ["UNKNOWN", "docx", "docm", "html", "pptx", "pptm", "xlsx", "xlsm"]
        if template_type not in allowed_values:
            raise ValueError(
                "Invalid value for `template_type` ({0}), must be one of {1}"
                    .format(template_type, allowed_values)
            )

        self._templateType = template_type

    @property
    def datasources(self):
        """Gets the datasources of this Metrics.

        All datasources that must be processed for this template.

        :return: The datasources of this Metrics.
        :rtype: list[str]
        """
        return self._datasources

    @datasources.setter
    def datasources(self, datasources):
        """Sets the datasources of this Metrics.

        All datasources that must be processed for this template.

        :param datasources: The datasources of this Metrics.
        :type: list[str]
        """

        # self._datasources.append(datasources)

        self._datasources = datasources
    @property
    def vars(self):
        """Gets the vars of this Metrics.  # noqa: E501

        All vars that must be defined by a caller in the template.  # noqa: E501

        :return: The vars of this Metrics.  # noqa: E501
        :rtype: list[str]
        """
        return self._vars

    @vars.setter
    def vars(self, vars):
        """Sets the vars of this Metrics.

        All vars that must be defined by a caller in the template.

        :param vars: The vars of this Metrics.
        :type: list[str]
        """

        self._vars = vars

    @property
    def variables(self):
        """Gets the variables of this Metrics.

        All of the template variables defined in the metadata.

        :return: The variables of this Metrics.
        :rtype: list[Variable]
        """
        return self._variables

    @variables.setter
    def variables(self, variables):
        """Sets the variables of this Metrics.

        All of the template variables defined in the metadata.

        :param variables: The variables of this Metrics.
        :type: list[Variable]

        """

        for variable in variables:
            defaultVals = []
            name=variable["Name"]if "Name" in variable else None
            description=variable["Description"]if "Description" in variable else None
            type = variable["Type"]if "Type" in variable else None
            required = variable["Required"]if "Required" in variable else None
            allowAll = variable["AllowAll"]if "AllowAll" in variable else None
            allowList = variable["AllowList"]if "AllowList" in variable else None
            allowFilter = variable["AllowFilter"]if "AllowFilter" in variable else None
            allowSort = variable["AllowSort"]if "AllowSort" in variable else None
            autoMeta = variable["AutoMetadata"]if "AutoMetadata" in variable else None
            allowedValues = variable["AllowedValues"]if "AllowedValues" in variable else None
            datasource = variable["Datasource"]if "Datasource" in variable else None
            calOffset = variable["CalOffset"] if "CallOffSet" in variable else None
            select = variable["Select"]if "Select" in variable else None
            selectFormat = variable["SelectFormat"]if "SelectFormat" in variable else None
            if "DefaultValues" in variable:
                for val in variable["DefaultValues"]:
                    label = val["Label"]if "Label" in val else None
                    name = val["Name"]if "Name" in val else None
                    if "Value" not in val:
                        value = None
                    else:
                        value = ParameterValue.ParameterValue(paramType=val["Value"]["ParamType"], rawValue=val["Value"]["RawValue"])
                valueReference = val["ValueReference"].lower()
                varValue = VariableValue.VariableValue(label=label, name=name, value=value, valueReference=valueReference)

                defaultVals.append(varValue)
            else:
                defaultVals = None
            variable = Variable.Variable(name=name, description=description, type=type, required=required, allowAll=allowAll, allowList=allowList, allowFilter=allowFilter, allowSort=allowSort, autoMetadata=autoMeta, defaultValues=defaultVals, allowedValues=allowedValues, datasource=datasource, calOffset=calOffset, select=select, selectFormat=selectFormat)
            self._variables.append(variable)

    @property
    def datasourceProfiles(self):
        """Gets the datasource_profiles of this Metrics.

        The child imports of this imported template.

        :return: The datasource_profiles of this Metrics.
        :rtype: list[DataSourceProfile]
        """
        return self._datasourceProfiles

    @datasourceProfiles.setter
    def datasourceProfiles(self, datasource_profiles):
        """Sets the datasource_profiles of this Metrics.

        The child imports of this imported template.

        :param datasource_profiles: The datasource_profiles of this Metrics.
        :type: list[DataSourceProfile]
        """
        for profile in datasource_profiles:

            props = []
            properties=profile["Properties"]


            for i in properties:
                props.append({i["Key"] : i["Value"]})
                if i["Key"] == "datasource-name":
                    name = i["Value"]
                elif i["Key"] == "connection-string":
                    rootPath = i["Value"]
                elif i["Key"] == "simple-type":
                    vendorType = i["Value"]

        self._datasourceProfiles.append(
            DataSourceProfile.DataSourceProfile(name=name, rootPath=rootPath, vendorType=vendorType, properties=props))


    @property
    def autotagVersion(self):
        """Gets the autotag_version of this Metrics.

        The version of the metadata. null if no metadata.

        :return: The autotag_version of this Metrics.
        :rtype: str
        """
        return self._autotagVersion

    @autotagVersion.setter
    def autotagVersion(self, autotag_version):
        """Sets the autotag_version of this Metrics.

        The version of the metadata. null if no metadata.

        :param autotag_version: The autotag_version of this Metrics.
        :type: str
        """

        self._autotagVersion = autotag_version

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
