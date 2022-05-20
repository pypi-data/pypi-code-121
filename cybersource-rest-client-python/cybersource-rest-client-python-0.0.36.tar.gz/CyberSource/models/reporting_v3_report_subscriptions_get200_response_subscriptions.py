# coding: utf-8

"""
    CyberSource Merged Spec

    All CyberSource API specs merged together. These are available at https://developer.cybersource.com/api/reference/api-reference.html

    OpenAPI spec version: 0.0.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class ReportingV3ReportSubscriptionsGet200ResponseSubscriptions(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'organization_id': 'str',
        'report_definition_id': 'str',
        'report_definition_name': 'str',
        'report_mime_type': 'str',
        'report_frequency': 'str',
        'report_interval': 'str',
        'report_name': 'str',
        'timezone': 'str',
        'start_time': 'datetime',
        'start_day': 'int',
        'report_fields': 'list[str]',
        'report_filters': 'dict(str, list[str])',
        'report_preferences': 'Reportingv3reportsReportPreferences',
        'group_id': 'str'
    }

    attribute_map = {
        'organization_id': 'organizationId',
        'report_definition_id': 'reportDefinitionId',
        'report_definition_name': 'reportDefinitionName',
        'report_mime_type': 'reportMimeType',
        'report_frequency': 'reportFrequency',
        'report_interval': 'reportInterval',
        'report_name': 'reportName',
        'timezone': 'timezone',
        'start_time': 'startTime',
        'start_day': 'startDay',
        'report_fields': 'reportFields',
        'report_filters': 'reportFilters',
        'report_preferences': 'reportPreferences',
        'group_id': 'groupId'
    }

    def __init__(self, organization_id=None, report_definition_id=None, report_definition_name=None, report_mime_type=None, report_frequency=None, report_interval=None, report_name=None, timezone=None, start_time=None, start_day=None, report_fields=None, report_filters=None, report_preferences=None, group_id=None):
        """
        ReportingV3ReportSubscriptionsGet200ResponseSubscriptions - a model defined in Swagger
        """

        self._organization_id = None
        self._report_definition_id = None
        self._report_definition_name = None
        self._report_mime_type = None
        self._report_frequency = None
        self._report_interval = None
        self._report_name = None
        self._timezone = None
        self._start_time = None
        self._start_day = None
        self._report_fields = None
        self._report_filters = None
        self._report_preferences = None
        self._group_id = None

        if organization_id is not None:
          self.organization_id = organization_id
        if report_definition_id is not None:
          self.report_definition_id = report_definition_id
        if report_definition_name is not None:
          self.report_definition_name = report_definition_name
        if report_mime_type is not None:
          self.report_mime_type = report_mime_type
        if report_frequency is not None:
          self.report_frequency = report_frequency
        if report_interval is not None:
          self.report_interval = report_interval
        if report_name is not None:
          self.report_name = report_name
        if timezone is not None:
          self.timezone = timezone
        if start_time is not None:
          self.start_time = start_time
        if start_day is not None:
          self.start_day = start_day
        if report_fields is not None:
          self.report_fields = report_fields
        if report_filters is not None:
          self.report_filters = report_filters
        if report_preferences is not None:
          self.report_preferences = report_preferences
        if group_id is not None:
          self.group_id = group_id

    @property
    def organization_id(self):
        """
        Gets the organization_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Selected Organization Id

        :return: The organization_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._organization_id

    @organization_id.setter
    def organization_id(self, organization_id):
        """
        Sets the organization_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Selected Organization Id

        :param organization_id: The organization_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._organization_id = organization_id

    @property
    def report_definition_id(self):
        """
        Gets the report_definition_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Definition Id

        :return: The report_definition_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._report_definition_id

    @report_definition_id.setter
    def report_definition_id(self, report_definition_id):
        """
        Sets the report_definition_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Definition Id

        :param report_definition_id: The report_definition_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._report_definition_id = report_definition_id

    @property
    def report_definition_name(self):
        """
        Gets the report_definition_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Definition Class

        :return: The report_definition_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._report_definition_name

    @report_definition_name.setter
    def report_definition_name(self, report_definition_name):
        """
        Sets the report_definition_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Definition Class

        :param report_definition_name: The report_definition_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._report_definition_name = report_definition_name

    @property
    def report_mime_type(self):
        """
        Gets the report_mime_type of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Format                          Valid values: - application/xml - text/csv 

        :return: The report_mime_type of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._report_mime_type

    @report_mime_type.setter
    def report_mime_type(self, report_mime_type):
        """
        Sets the report_mime_type of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Format                          Valid values: - application/xml - text/csv 

        :param report_mime_type: The report_mime_type of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._report_mime_type = report_mime_type

    @property
    def report_frequency(self):
        """
        Gets the report_frequency of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        'Report Frequency' **NOTE: Do not document USER_DEFINED Frequency field in developer center**  Valid values: - DAILY - WEEKLY - MONTHLY - USER_DEFINED 

        :return: The report_frequency of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._report_frequency

    @report_frequency.setter
    def report_frequency(self, report_frequency):
        """
        Sets the report_frequency of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        'Report Frequency' **NOTE: Do not document USER_DEFINED Frequency field in developer center**  Valid values: - DAILY - WEEKLY - MONTHLY - USER_DEFINED 

        :param report_frequency: The report_frequency of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._report_frequency = report_frequency

    @property
    def report_interval(self):
        """
        Gets the report_interval of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        If the reportFrequency is User-defined, reportInterval should be in **ISO 8601 time format** Please refer the following link to know more about ISO 8601 format.[Rfc Time Format](https://en.wikipedia.org/wiki/ISO_8601#Durations)  **Example time format for 2 hours and 30 Mins:**   - PT2H30M **NOTE: Do not document reportInterval field in developer center** 

        :return: The report_interval of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._report_interval

    @report_interval.setter
    def report_interval(self, report_interval):
        """
        Sets the report_interval of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        If the reportFrequency is User-defined, reportInterval should be in **ISO 8601 time format** Please refer the following link to know more about ISO 8601 format.[Rfc Time Format](https://en.wikipedia.org/wiki/ISO_8601#Durations)  **Example time format for 2 hours and 30 Mins:**   - PT2H30M **NOTE: Do not document reportInterval field in developer center** 

        :param report_interval: The report_interval of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """
        if report_interval is not None and not re.search('^PT((([1-9]|1[0-9]|2[0-3])H(([1-9]|[1-4][0-9]|5[0-9])M)?)|((([1-9]|1[0-9]|2[0-3])H)?([1-9]|[1-4][0-9]|5[0-9])M))$', report_interval):
            raise ValueError("Invalid value for `report_interval`, must be a follow pattern or equal to `/^PT((([1-9]|1[0-9]|2[0-3])H(([1-9]|[1-4][0-9]|5[0-9])M)?)|((([1-9]|1[0-9]|2[0-3])H)?([1-9]|[1-4][0-9]|5[0-9])M))$/`")

        self._report_interval = report_interval

    @property
    def report_name(self):
        """
        Gets the report_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Name

        :return: The report_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._report_name

    @report_name.setter
    def report_name(self, report_name):
        """
        Sets the report_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Report Name

        :param report_name: The report_name of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._report_name = report_name

    @property
    def timezone(self):
        """
        Gets the timezone of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Time Zone

        :return: The timezone of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """
        Sets the timezone of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Time Zone

        :param timezone: The timezone of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._timezone = timezone

    @property
    def start_time(self):
        """
        Gets the start_time of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Start Time

        :return: The start_time of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: datetime
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """
        Sets the start_time of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Start Time

        :param start_time: The start_time of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: datetime
        """

        self._start_time = start_time

    @property
    def start_day(self):
        """
        Gets the start_day of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Start Day

        :return: The start_day of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: int
        """
        return self._start_day

    @start_day.setter
    def start_day(self, start_day):
        """
        Sets the start_day of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Start Day

        :param start_day: The start_day of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: int
        """

        self._start_day = start_day

    @property
    def report_fields(self):
        """
        Gets the report_fields of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        List of all fields String values

        :return: The report_fields of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: list[str]
        """
        return self._report_fields

    @report_fields.setter
    def report_fields(self, report_fields):
        """
        Sets the report_fields of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        List of all fields String values

        :param report_fields: The report_fields of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: list[str]
        """

        self._report_fields = report_fields

    @property
    def report_filters(self):
        """
        Gets the report_filters of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        List of filters to apply

        :return: The report_filters of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: dict(str, list[str])
        """
        return self._report_filters

    @report_filters.setter
    def report_filters(self, report_filters):
        """
        Sets the report_filters of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        List of filters to apply

        :param report_filters: The report_filters of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: dict(str, list[str])
        """

        self._report_filters = report_filters

    @property
    def report_preferences(self):
        """
        Gets the report_preferences of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.

        :return: The report_preferences of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: Reportingv3reportsReportPreferences
        """
        return self._report_preferences

    @report_preferences.setter
    def report_preferences(self, report_preferences):
        """
        Sets the report_preferences of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.

        :param report_preferences: The report_preferences of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: Reportingv3reportsReportPreferences
        """

        self._report_preferences = report_preferences

    @property
    def group_id(self):
        """
        Gets the group_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Id for the selected group.

        :return: The group_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :rtype: str
        """
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        """
        Sets the group_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        Id for the selected group.

        :param group_id: The group_id of this ReportingV3ReportSubscriptionsGet200ResponseSubscriptions.
        :type: str
        """

        self._group_id = group_id

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, ReportingV3ReportSubscriptionsGet200ResponseSubscriptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
