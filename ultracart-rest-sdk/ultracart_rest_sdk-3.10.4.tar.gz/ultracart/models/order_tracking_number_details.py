# coding: utf-8

"""
    UltraCart Rest API V2

    UltraCart REST API Version 2  # noqa: E501

    OpenAPI spec version: 2.0.0
    Contact: support@ultracart.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class OrderTrackingNumberDetails(object):
    """NOTE: This class is auto generated by the swagger code generator program.

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
        'actual_delivery_date': 'str',
        'actual_delivery_date_formatted': 'str',
        'details': 'list[OrderTrackingNumberDetail]',
        'easypost_tracker_id': 'str',
        'expected_delivery_date': 'str',
        'expected_delivery_date_formatted': 'str',
        'map_url': 'str',
        'order_placed_date': 'str',
        'order_placed_date_formatted': 'str',
        'payment_processed_date': 'str',
        'payment_processed_date_formatted': 'str',
        'shipped_date': 'str',
        'shipped_date_formatted': 'str',
        'shipping_method': 'str',
        'status': 'str',
        'status_description': 'str',
        'tracking_number': 'str',
        'tracking_url': 'str'
    }

    attribute_map = {
        'actual_delivery_date': 'actual_delivery_date',
        'actual_delivery_date_formatted': 'actual_delivery_date_formatted',
        'details': 'details',
        'easypost_tracker_id': 'easypost_tracker_id',
        'expected_delivery_date': 'expected_delivery_date',
        'expected_delivery_date_formatted': 'expected_delivery_date_formatted',
        'map_url': 'map_url',
        'order_placed_date': 'order_placed_date',
        'order_placed_date_formatted': 'order_placed_date_formatted',
        'payment_processed_date': 'payment_processed_date',
        'payment_processed_date_formatted': 'payment_processed_date_formatted',
        'shipped_date': 'shipped_date',
        'shipped_date_formatted': 'shipped_date_formatted',
        'shipping_method': 'shipping_method',
        'status': 'status',
        'status_description': 'status_description',
        'tracking_number': 'tracking_number',
        'tracking_url': 'tracking_url'
    }

    def __init__(self, actual_delivery_date=None, actual_delivery_date_formatted=None, details=None, easypost_tracker_id=None, expected_delivery_date=None, expected_delivery_date_formatted=None, map_url=None, order_placed_date=None, order_placed_date_formatted=None, payment_processed_date=None, payment_processed_date_formatted=None, shipped_date=None, shipped_date_formatted=None, shipping_method=None, status=None, status_description=None, tracking_number=None, tracking_url=None):  # noqa: E501
        """OrderTrackingNumberDetails - a model defined in Swagger"""  # noqa: E501

        self._actual_delivery_date = None
        self._actual_delivery_date_formatted = None
        self._details = None
        self._easypost_tracker_id = None
        self._expected_delivery_date = None
        self._expected_delivery_date_formatted = None
        self._map_url = None
        self._order_placed_date = None
        self._order_placed_date_formatted = None
        self._payment_processed_date = None
        self._payment_processed_date_formatted = None
        self._shipped_date = None
        self._shipped_date_formatted = None
        self._shipping_method = None
        self._status = None
        self._status_description = None
        self._tracking_number = None
        self._tracking_url = None
        self.discriminator = None

        if actual_delivery_date is not None:
            self.actual_delivery_date = actual_delivery_date
        if actual_delivery_date_formatted is not None:
            self.actual_delivery_date_formatted = actual_delivery_date_formatted
        if details is not None:
            self.details = details
        if easypost_tracker_id is not None:
            self.easypost_tracker_id = easypost_tracker_id
        if expected_delivery_date is not None:
            self.expected_delivery_date = expected_delivery_date
        if expected_delivery_date_formatted is not None:
            self.expected_delivery_date_formatted = expected_delivery_date_formatted
        if map_url is not None:
            self.map_url = map_url
        if order_placed_date is not None:
            self.order_placed_date = order_placed_date
        if order_placed_date_formatted is not None:
            self.order_placed_date_formatted = order_placed_date_formatted
        if payment_processed_date is not None:
            self.payment_processed_date = payment_processed_date
        if payment_processed_date_formatted is not None:
            self.payment_processed_date_formatted = payment_processed_date_formatted
        if shipped_date is not None:
            self.shipped_date = shipped_date
        if shipped_date_formatted is not None:
            self.shipped_date_formatted = shipped_date_formatted
        if shipping_method is not None:
            self.shipping_method = shipping_method
        if status is not None:
            self.status = status
        if status_description is not None:
            self.status_description = status_description
        if tracking_number is not None:
            self.tracking_number = tracking_number
        if tracking_url is not None:
            self.tracking_url = tracking_url

    @property
    def actual_delivery_date(self):
        """Gets the actual_delivery_date of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The actual_delivery_date of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._actual_delivery_date

    @actual_delivery_date.setter
    def actual_delivery_date(self, actual_delivery_date):
        """Sets the actual_delivery_date of this OrderTrackingNumberDetails.


        :param actual_delivery_date: The actual_delivery_date of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._actual_delivery_date = actual_delivery_date

    @property
    def actual_delivery_date_formatted(self):
        """Gets the actual_delivery_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The actual_delivery_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._actual_delivery_date_formatted

    @actual_delivery_date_formatted.setter
    def actual_delivery_date_formatted(self, actual_delivery_date_formatted):
        """Sets the actual_delivery_date_formatted of this OrderTrackingNumberDetails.


        :param actual_delivery_date_formatted: The actual_delivery_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._actual_delivery_date_formatted = actual_delivery_date_formatted

    @property
    def details(self):
        """Gets the details of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The details of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: list[OrderTrackingNumberDetail]
        """
        return self._details

    @details.setter
    def details(self, details):
        """Sets the details of this OrderTrackingNumberDetails.


        :param details: The details of this OrderTrackingNumberDetails.  # noqa: E501
        :type: list[OrderTrackingNumberDetail]
        """

        self._details = details

    @property
    def easypost_tracker_id(self):
        """Gets the easypost_tracker_id of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The easypost_tracker_id of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._easypost_tracker_id

    @easypost_tracker_id.setter
    def easypost_tracker_id(self, easypost_tracker_id):
        """Sets the easypost_tracker_id of this OrderTrackingNumberDetails.


        :param easypost_tracker_id: The easypost_tracker_id of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._easypost_tracker_id = easypost_tracker_id

    @property
    def expected_delivery_date(self):
        """Gets the expected_delivery_date of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The expected_delivery_date of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._expected_delivery_date

    @expected_delivery_date.setter
    def expected_delivery_date(self, expected_delivery_date):
        """Sets the expected_delivery_date of this OrderTrackingNumberDetails.


        :param expected_delivery_date: The expected_delivery_date of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._expected_delivery_date = expected_delivery_date

    @property
    def expected_delivery_date_formatted(self):
        """Gets the expected_delivery_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The expected_delivery_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._expected_delivery_date_formatted

    @expected_delivery_date_formatted.setter
    def expected_delivery_date_formatted(self, expected_delivery_date_formatted):
        """Sets the expected_delivery_date_formatted of this OrderTrackingNumberDetails.


        :param expected_delivery_date_formatted: The expected_delivery_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._expected_delivery_date_formatted = expected_delivery_date_formatted

    @property
    def map_url(self):
        """Gets the map_url of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The map_url of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._map_url

    @map_url.setter
    def map_url(self, map_url):
        """Sets the map_url of this OrderTrackingNumberDetails.


        :param map_url: The map_url of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._map_url = map_url

    @property
    def order_placed_date(self):
        """Gets the order_placed_date of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The order_placed_date of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._order_placed_date

    @order_placed_date.setter
    def order_placed_date(self, order_placed_date):
        """Sets the order_placed_date of this OrderTrackingNumberDetails.


        :param order_placed_date: The order_placed_date of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._order_placed_date = order_placed_date

    @property
    def order_placed_date_formatted(self):
        """Gets the order_placed_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The order_placed_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._order_placed_date_formatted

    @order_placed_date_formatted.setter
    def order_placed_date_formatted(self, order_placed_date_formatted):
        """Sets the order_placed_date_formatted of this OrderTrackingNumberDetails.


        :param order_placed_date_formatted: The order_placed_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._order_placed_date_formatted = order_placed_date_formatted

    @property
    def payment_processed_date(self):
        """Gets the payment_processed_date of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The payment_processed_date of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._payment_processed_date

    @payment_processed_date.setter
    def payment_processed_date(self, payment_processed_date):
        """Sets the payment_processed_date of this OrderTrackingNumberDetails.


        :param payment_processed_date: The payment_processed_date of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._payment_processed_date = payment_processed_date

    @property
    def payment_processed_date_formatted(self):
        """Gets the payment_processed_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The payment_processed_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._payment_processed_date_formatted

    @payment_processed_date_formatted.setter
    def payment_processed_date_formatted(self, payment_processed_date_formatted):
        """Sets the payment_processed_date_formatted of this OrderTrackingNumberDetails.


        :param payment_processed_date_formatted: The payment_processed_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._payment_processed_date_formatted = payment_processed_date_formatted

    @property
    def shipped_date(self):
        """Gets the shipped_date of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The shipped_date of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._shipped_date

    @shipped_date.setter
    def shipped_date(self, shipped_date):
        """Sets the shipped_date of this OrderTrackingNumberDetails.


        :param shipped_date: The shipped_date of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._shipped_date = shipped_date

    @property
    def shipped_date_formatted(self):
        """Gets the shipped_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The shipped_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._shipped_date_formatted

    @shipped_date_formatted.setter
    def shipped_date_formatted(self, shipped_date_formatted):
        """Sets the shipped_date_formatted of this OrderTrackingNumberDetails.


        :param shipped_date_formatted: The shipped_date_formatted of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._shipped_date_formatted = shipped_date_formatted

    @property
    def shipping_method(self):
        """Gets the shipping_method of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The shipping_method of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._shipping_method

    @shipping_method.setter
    def shipping_method(self, shipping_method):
        """Sets the shipping_method of this OrderTrackingNumberDetails.


        :param shipping_method: The shipping_method of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._shipping_method = shipping_method

    @property
    def status(self):
        """Gets the status of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The status of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this OrderTrackingNumberDetails.


        :param status: The status of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def status_description(self):
        """Gets the status_description of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The status_description of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._status_description

    @status_description.setter
    def status_description(self, status_description):
        """Sets the status_description of this OrderTrackingNumberDetails.


        :param status_description: The status_description of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._status_description = status_description

    @property
    def tracking_number(self):
        """Gets the tracking_number of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The tracking_number of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._tracking_number

    @tracking_number.setter
    def tracking_number(self, tracking_number):
        """Sets the tracking_number of this OrderTrackingNumberDetails.


        :param tracking_number: The tracking_number of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._tracking_number = tracking_number

    @property
    def tracking_url(self):
        """Gets the tracking_url of this OrderTrackingNumberDetails.  # noqa: E501


        :return: The tracking_url of this OrderTrackingNumberDetails.  # noqa: E501
        :rtype: str
        """
        return self._tracking_url

    @tracking_url.setter
    def tracking_url(self, tracking_url):
        """Sets the tracking_url of this OrderTrackingNumberDetails.


        :param tracking_url: The tracking_url of this OrderTrackingNumberDetails.  # noqa: E501
        :type: str
        """

        self._tracking_url = tracking_url

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if issubclass(OrderTrackingNumberDetails, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, OrderTrackingNumberDetails):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
