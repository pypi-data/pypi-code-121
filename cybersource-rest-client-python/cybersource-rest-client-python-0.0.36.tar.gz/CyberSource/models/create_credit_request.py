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


class CreateCreditRequest(object):
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
        'client_reference_information': 'Ptsv2paymentsClientReferenceInformation',
        'processing_information': 'Ptsv2creditsProcessingInformation',
        'payment_information': 'Ptsv2paymentsidrefundsPaymentInformation',
        'order_information': 'Ptsv2paymentsidrefundsOrderInformation',
        'buyer_information': 'Ptsv2paymentsidcapturesBuyerInformation',
        'device_information': 'Ptsv2paymentsidcapturesDeviceInformation',
        'merchant_information': 'Ptsv2paymentsidrefundsMerchantInformation',
        'aggregator_information': 'Ptsv2paymentsidcapturesAggregatorInformation',
        'point_of_sale_information': 'Ptsv2paymentsPointOfSaleInformation',
        'merchant_defined_information': 'list[Ptsv2paymentsMerchantDefinedInformation]',
        'installment_information': 'Ptsv2creditsInstallmentInformation',
        'travel_information': 'Ptsv2paymentsTravelInformation',
        'promotion_information': 'Ptsv2paymentsPromotionInformation'
    }

    attribute_map = {
        'client_reference_information': 'clientReferenceInformation',
        'processing_information': 'processingInformation',
        'payment_information': 'paymentInformation',
        'order_information': 'orderInformation',
        'buyer_information': 'buyerInformation',
        'device_information': 'deviceInformation',
        'merchant_information': 'merchantInformation',
        'aggregator_information': 'aggregatorInformation',
        'point_of_sale_information': 'pointOfSaleInformation',
        'merchant_defined_information': 'merchantDefinedInformation',
        'installment_information': 'installmentInformation',
        'travel_information': 'travelInformation',
        'promotion_information': 'promotionInformation'
    }

    def __init__(self, client_reference_information=None, processing_information=None, payment_information=None, order_information=None, buyer_information=None, device_information=None, merchant_information=None, aggregator_information=None, point_of_sale_information=None, merchant_defined_information=None, installment_information=None, travel_information=None, promotion_information=None):
        """
        CreateCreditRequest - a model defined in Swagger
        """

        self._client_reference_information = None
        self._processing_information = None
        self._payment_information = None
        self._order_information = None
        self._buyer_information = None
        self._device_information = None
        self._merchant_information = None
        self._aggregator_information = None
        self._point_of_sale_information = None
        self._merchant_defined_information = None
        self._installment_information = None
        self._travel_information = None
        self._promotion_information = None

        if client_reference_information is not None:
          self.client_reference_information = client_reference_information
        if processing_information is not None:
          self.processing_information = processing_information
        if payment_information is not None:
          self.payment_information = payment_information
        if order_information is not None:
          self.order_information = order_information
        if buyer_information is not None:
          self.buyer_information = buyer_information
        if device_information is not None:
          self.device_information = device_information
        if merchant_information is not None:
          self.merchant_information = merchant_information
        if aggregator_information is not None:
          self.aggregator_information = aggregator_information
        if point_of_sale_information is not None:
          self.point_of_sale_information = point_of_sale_information
        if merchant_defined_information is not None:
          self.merchant_defined_information = merchant_defined_information
        if installment_information is not None:
          self.installment_information = installment_information
        if travel_information is not None:
          self.travel_information = travel_information
        if promotion_information is not None:
          self.promotion_information = promotion_information

    @property
    def client_reference_information(self):
        """
        Gets the client_reference_information of this CreateCreditRequest.

        :return: The client_reference_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsClientReferenceInformation
        """
        return self._client_reference_information

    @client_reference_information.setter
    def client_reference_information(self, client_reference_information):
        """
        Sets the client_reference_information of this CreateCreditRequest.

        :param client_reference_information: The client_reference_information of this CreateCreditRequest.
        :type: Ptsv2paymentsClientReferenceInformation
        """

        self._client_reference_information = client_reference_information

    @property
    def processing_information(self):
        """
        Gets the processing_information of this CreateCreditRequest.

        :return: The processing_information of this CreateCreditRequest.
        :rtype: Ptsv2creditsProcessingInformation
        """
        return self._processing_information

    @processing_information.setter
    def processing_information(self, processing_information):
        """
        Sets the processing_information of this CreateCreditRequest.

        :param processing_information: The processing_information of this CreateCreditRequest.
        :type: Ptsv2creditsProcessingInformation
        """

        self._processing_information = processing_information

    @property
    def payment_information(self):
        """
        Gets the payment_information of this CreateCreditRequest.

        :return: The payment_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsidrefundsPaymentInformation
        """
        return self._payment_information

    @payment_information.setter
    def payment_information(self, payment_information):
        """
        Sets the payment_information of this CreateCreditRequest.

        :param payment_information: The payment_information of this CreateCreditRequest.
        :type: Ptsv2paymentsidrefundsPaymentInformation
        """

        self._payment_information = payment_information

    @property
    def order_information(self):
        """
        Gets the order_information of this CreateCreditRequest.

        :return: The order_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsidrefundsOrderInformation
        """
        return self._order_information

    @order_information.setter
    def order_information(self, order_information):
        """
        Sets the order_information of this CreateCreditRequest.

        :param order_information: The order_information of this CreateCreditRequest.
        :type: Ptsv2paymentsidrefundsOrderInformation
        """

        self._order_information = order_information

    @property
    def buyer_information(self):
        """
        Gets the buyer_information of this CreateCreditRequest.

        :return: The buyer_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsidcapturesBuyerInformation
        """
        return self._buyer_information

    @buyer_information.setter
    def buyer_information(self, buyer_information):
        """
        Sets the buyer_information of this CreateCreditRequest.

        :param buyer_information: The buyer_information of this CreateCreditRequest.
        :type: Ptsv2paymentsidcapturesBuyerInformation
        """

        self._buyer_information = buyer_information

    @property
    def device_information(self):
        """
        Gets the device_information of this CreateCreditRequest.

        :return: The device_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsidcapturesDeviceInformation
        """
        return self._device_information

    @device_information.setter
    def device_information(self, device_information):
        """
        Sets the device_information of this CreateCreditRequest.

        :param device_information: The device_information of this CreateCreditRequest.
        :type: Ptsv2paymentsidcapturesDeviceInformation
        """

        self._device_information = device_information

    @property
    def merchant_information(self):
        """
        Gets the merchant_information of this CreateCreditRequest.

        :return: The merchant_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsidrefundsMerchantInformation
        """
        return self._merchant_information

    @merchant_information.setter
    def merchant_information(self, merchant_information):
        """
        Sets the merchant_information of this CreateCreditRequest.

        :param merchant_information: The merchant_information of this CreateCreditRequest.
        :type: Ptsv2paymentsidrefundsMerchantInformation
        """

        self._merchant_information = merchant_information

    @property
    def aggregator_information(self):
        """
        Gets the aggregator_information of this CreateCreditRequest.

        :return: The aggregator_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsidcapturesAggregatorInformation
        """
        return self._aggregator_information

    @aggregator_information.setter
    def aggregator_information(self, aggregator_information):
        """
        Sets the aggregator_information of this CreateCreditRequest.

        :param aggregator_information: The aggregator_information of this CreateCreditRequest.
        :type: Ptsv2paymentsidcapturesAggregatorInformation
        """

        self._aggregator_information = aggregator_information

    @property
    def point_of_sale_information(self):
        """
        Gets the point_of_sale_information of this CreateCreditRequest.

        :return: The point_of_sale_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsPointOfSaleInformation
        """
        return self._point_of_sale_information

    @point_of_sale_information.setter
    def point_of_sale_information(self, point_of_sale_information):
        """
        Sets the point_of_sale_information of this CreateCreditRequest.

        :param point_of_sale_information: The point_of_sale_information of this CreateCreditRequest.
        :type: Ptsv2paymentsPointOfSaleInformation
        """

        self._point_of_sale_information = point_of_sale_information

    @property
    def merchant_defined_information(self):
        """
        Gets the merchant_defined_information of this CreateCreditRequest.
        The object containing the custom data that the merchant defines. 

        :return: The merchant_defined_information of this CreateCreditRequest.
        :rtype: list[Ptsv2paymentsMerchantDefinedInformation]
        """
        return self._merchant_defined_information

    @merchant_defined_information.setter
    def merchant_defined_information(self, merchant_defined_information):
        """
        Sets the merchant_defined_information of this CreateCreditRequest.
        The object containing the custom data that the merchant defines. 

        :param merchant_defined_information: The merchant_defined_information of this CreateCreditRequest.
        :type: list[Ptsv2paymentsMerchantDefinedInformation]
        """

        self._merchant_defined_information = merchant_defined_information

    @property
    def installment_information(self):
        """
        Gets the installment_information of this CreateCreditRequest.

        :return: The installment_information of this CreateCreditRequest.
        :rtype: Ptsv2creditsInstallmentInformation
        """
        return self._installment_information

    @installment_information.setter
    def installment_information(self, installment_information):
        """
        Sets the installment_information of this CreateCreditRequest.

        :param installment_information: The installment_information of this CreateCreditRequest.
        :type: Ptsv2creditsInstallmentInformation
        """

        self._installment_information = installment_information

    @property
    def travel_information(self):
        """
        Gets the travel_information of this CreateCreditRequest.

        :return: The travel_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsTravelInformation
        """
        return self._travel_information

    @travel_information.setter
    def travel_information(self, travel_information):
        """
        Sets the travel_information of this CreateCreditRequest.

        :param travel_information: The travel_information of this CreateCreditRequest.
        :type: Ptsv2paymentsTravelInformation
        """

        self._travel_information = travel_information

    @property
    def promotion_information(self):
        """
        Gets the promotion_information of this CreateCreditRequest.

        :return: The promotion_information of this CreateCreditRequest.
        :rtype: Ptsv2paymentsPromotionInformation
        """
        return self._promotion_information

    @promotion_information.setter
    def promotion_information(self, promotion_information):
        """
        Sets the promotion_information of this CreateCreditRequest.

        :param promotion_information: The promotion_information of this CreateCreditRequest.
        :type: Ptsv2paymentsPromotionInformation
        """

        self._promotion_information = promotion_information

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
        if not isinstance(other, CreateCreditRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
