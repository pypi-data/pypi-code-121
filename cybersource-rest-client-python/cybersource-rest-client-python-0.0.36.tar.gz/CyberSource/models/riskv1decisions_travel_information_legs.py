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


class Riskv1decisionsTravelInformationLegs(object):
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
        'origination': 'str',
        'destination': 'str',
        'carrier_code': 'str',
        'departure_date': 'str'
    }

    attribute_map = {
        'origination': 'origination',
        'destination': 'destination',
        'carrier_code': 'carrierCode',
        'departure_date': 'departureDate'
    }

    def __init__(self, origination=None, destination=None, carrier_code=None, departure_date=None):
        """
        Riskv1decisionsTravelInformationLegs - a model defined in Swagger
        """

        self._origination = None
        self._destination = None
        self._carrier_code = None
        self._departure_date = None

        if origination is not None:
          self.origination = origination
        if destination is not None:
          self.destination = destination
        if carrier_code is not None:
          self.carrier_code = carrier_code
        if departure_date is not None:
          self.departure_date = departure_date

    @property
    def origination(self):
        """
        Gets the origination of this Riskv1decisionsTravelInformationLegs.
        Use to specify the airport code for the origin of the leg of the trip, which is designated by the pound (#) symbol in the field name. This code is usually three digits long, for example: SFO = San Francisco. Do not use the colon (:) or the dash (-). For airport codes, see the IATA Airline and Airport Code Search. The leg number can be a positive integer from 0 to N. For example: `travelInformation.legs.0.origination=SFO` `travelInformation.legs.1.origination=SFO`  **Note** In your request, send either the complete route or the individual legs (`legs.0.origination` and `legs.n.destination`). If you send all the fields, the complete route takes precedence over the individual legs.  For details, see the `decision_manager_travel_leg#_orig` field description in _Decision Manager Using the SCMP API Developer Guide_ on the [CyberSource Business Center.](https://ebc2.cybersource.com/ebc2/) Click **Decision Manager** > **Documentation** > **Guides** > _Decision Manager Using the SCMP API Developer Guide_ (PDF link). 

        :return: The origination of this Riskv1decisionsTravelInformationLegs.
        :rtype: str
        """
        return self._origination

    @origination.setter
    def origination(self, origination):
        """
        Sets the origination of this Riskv1decisionsTravelInformationLegs.
        Use to specify the airport code for the origin of the leg of the trip, which is designated by the pound (#) symbol in the field name. This code is usually three digits long, for example: SFO = San Francisco. Do not use the colon (:) or the dash (-). For airport codes, see the IATA Airline and Airport Code Search. The leg number can be a positive integer from 0 to N. For example: `travelInformation.legs.0.origination=SFO` `travelInformation.legs.1.origination=SFO`  **Note** In your request, send either the complete route or the individual legs (`legs.0.origination` and `legs.n.destination`). If you send all the fields, the complete route takes precedence over the individual legs.  For details, see the `decision_manager_travel_leg#_orig` field description in _Decision Manager Using the SCMP API Developer Guide_ on the [CyberSource Business Center.](https://ebc2.cybersource.com/ebc2/) Click **Decision Manager** > **Documentation** > **Guides** > _Decision Manager Using the SCMP API Developer Guide_ (PDF link). 

        :param origination: The origination of this Riskv1decisionsTravelInformationLegs.
        :type: str
        """

        self._origination = origination

    @property
    def destination(self):
        """
        Gets the destination of this Riskv1decisionsTravelInformationLegs.
        Use to specify the airport code for the destination of the leg of the trip, which is designated by the pound (#) symbol in the field name. This code is usually three digits long, for example: SFO = San Francisco. Do not use the colon (:) or the dash (-). For airport codes, see [IATA Airline and Airport Code Search](https://www.iata.org/publications/Pages/code-search.aspx). The leg number can be a positive integer from 0 to N. For example:  `travelInformation.legs.0.destination=SFO` `travelInformation.legs.1.destination=SFO`  **Note** In your request, send either the complete route or the individual legs (`legs.0.origination` and `legs.n.destination`). If you send all the fields, the complete route takes precedence over the individual legs.  For details, see the `decision_manager_travel_leg#_dest` field description in _Decision Manager Using the SCMP API Developer Guide_ on the [CyberSource Business Center.](https://ebc2.cybersource.com/ebc2/) Click **Decision Manager** > **Documentation** > **Guides** > _Decision Manager Using the SCMP API Developer Guide_ (PDF link). 

        :return: The destination of this Riskv1decisionsTravelInformationLegs.
        :rtype: str
        """
        return self._destination

    @destination.setter
    def destination(self, destination):
        """
        Sets the destination of this Riskv1decisionsTravelInformationLegs.
        Use to specify the airport code for the destination of the leg of the trip, which is designated by the pound (#) symbol in the field name. This code is usually three digits long, for example: SFO = San Francisco. Do not use the colon (:) or the dash (-). For airport codes, see [IATA Airline and Airport Code Search](https://www.iata.org/publications/Pages/code-search.aspx). The leg number can be a positive integer from 0 to N. For example:  `travelInformation.legs.0.destination=SFO` `travelInformation.legs.1.destination=SFO`  **Note** In your request, send either the complete route or the individual legs (`legs.0.origination` and `legs.n.destination`). If you send all the fields, the complete route takes precedence over the individual legs.  For details, see the `decision_manager_travel_leg#_dest` field description in _Decision Manager Using the SCMP API Developer Guide_ on the [CyberSource Business Center.](https://ebc2.cybersource.com/ebc2/) Click **Decision Manager** > **Documentation** > **Guides** > _Decision Manager Using the SCMP API Developer Guide_ (PDF link). 

        :param destination: The destination of this Riskv1decisionsTravelInformationLegs.
        :type: str
        """

        self._destination = destination

    @property
    def carrier_code(self):
        """
        Gets the carrier_code of this Riskv1decisionsTravelInformationLegs.
        International Air Transport Association (IATA) code for the carrier for this leg of the trip. Required for each leg. Required for American Express SafeKey (U.S.) for travel-related requests. 

        :return: The carrier_code of this Riskv1decisionsTravelInformationLegs.
        :rtype: str
        """
        return self._carrier_code

    @carrier_code.setter
    def carrier_code(self, carrier_code):
        """
        Sets the carrier_code of this Riskv1decisionsTravelInformationLegs.
        International Air Transport Association (IATA) code for the carrier for this leg of the trip. Required for each leg. Required for American Express SafeKey (U.S.) for travel-related requests. 

        :param carrier_code: The carrier_code of this Riskv1decisionsTravelInformationLegs.
        :type: str
        """

        self._carrier_code = carrier_code

    @property
    def departure_date(self):
        """
        Gets the departure_date of this Riskv1decisionsTravelInformationLegs.
        Departure date for the first leg of the trip. Format: YYYYMMDD. Required for American Express SafeKey (U.S.) for travel-related requests. 

        :return: The departure_date of this Riskv1decisionsTravelInformationLegs.
        :rtype: str
        """
        return self._departure_date

    @departure_date.setter
    def departure_date(self, departure_date):
        """
        Sets the departure_date of this Riskv1decisionsTravelInformationLegs.
        Departure date for the first leg of the trip. Format: YYYYMMDD. Required for American Express SafeKey (U.S.) for travel-related requests. 

        :param departure_date: The departure_date of this Riskv1decisionsTravelInformationLegs.
        :type: str
        """

        self._departure_date = departure_date

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
        if not isinstance(other, Riskv1decisionsTravelInformationLegs):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
