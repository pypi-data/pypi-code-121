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


class Riskv1decisionsOrderInformationLineItems(object):
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
        'total_amount': 'str',
        'unit_price': 'str',
        'quantity': 'int',
        'gift_card_currency': 'int',
        'product_sku': 'str',
        'product_risk': 'str',
        'product_description': 'str',
        'product_name': 'str',
        'product_code': 'str',
        'gift': 'bool',
        'distributor_product_sku': 'str',
        'passenger': 'Ptsv2paymentsOrderInformationPassenger',
        'shipping_destination_types': 'str',
        'tax_amount': 'str'
    }

    attribute_map = {
        'total_amount': 'totalAmount',
        'unit_price': 'unitPrice',
        'quantity': 'quantity',
        'gift_card_currency': 'giftCardCurrency',
        'product_sku': 'productSKU',
        'product_risk': 'productRisk',
        'product_description': 'productDescription',
        'product_name': 'productName',
        'product_code': 'productCode',
        'gift': 'gift',
        'distributor_product_sku': 'distributorProductSku',
        'passenger': 'passenger',
        'shipping_destination_types': 'shippingDestinationTypes',
        'tax_amount': 'taxAmount'
    }

    def __init__(self, total_amount=None, unit_price=None, quantity=None, gift_card_currency=None, product_sku=None, product_risk=None, product_description=None, product_name=None, product_code=None, gift=None, distributor_product_sku=None, passenger=None, shipping_destination_types=None, tax_amount=None):
        """
        Riskv1decisionsOrderInformationLineItems - a model defined in Swagger
        """

        self._total_amount = None
        self._unit_price = None
        self._quantity = None
        self._gift_card_currency = None
        self._product_sku = None
        self._product_risk = None
        self._product_description = None
        self._product_name = None
        self._product_code = None
        self._gift = None
        self._distributor_product_sku = None
        self._passenger = None
        self._shipping_destination_types = None
        self._tax_amount = None

        if total_amount is not None:
          self.total_amount = total_amount
        if unit_price is not None:
          self.unit_price = unit_price
        if quantity is not None:
          self.quantity = quantity
        if gift_card_currency is not None:
          self.gift_card_currency = gift_card_currency
        if product_sku is not None:
          self.product_sku = product_sku
        if product_risk is not None:
          self.product_risk = product_risk
        if product_description is not None:
          self.product_description = product_description
        if product_name is not None:
          self.product_name = product_name
        if product_code is not None:
          self.product_code = product_code
        if gift is not None:
          self.gift = gift
        if distributor_product_sku is not None:
          self.distributor_product_sku = distributor_product_sku
        if passenger is not None:
          self.passenger = passenger
        if shipping_destination_types is not None:
          self.shipping_destination_types = shipping_destination_types
        if tax_amount is not None:
          self.tax_amount = tax_amount

    @property
    def total_amount(self):
        """
        Gets the total_amount of this Riskv1decisionsOrderInformationLineItems.
        Total amount for the item. Normally calculated as the unit price times quantity.  When `orderInformation.lineItems[].productCode` is \"gift_card\", this is the purchase amount total for prepaid gift cards in major units.  Example: 123.45 USD = 123 

        :return: The total_amount of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._total_amount

    @total_amount.setter
    def total_amount(self, total_amount):
        """
        Sets the total_amount of this Riskv1decisionsOrderInformationLineItems.
        Total amount for the item. Normally calculated as the unit price times quantity.  When `orderInformation.lineItems[].productCode` is \"gift_card\", this is the purchase amount total for prepaid gift cards in major units.  Example: 123.45 USD = 123 

        :param total_amount: The total_amount of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._total_amount = total_amount

    @property
    def unit_price(self):
        """
        Gets the unit_price of this Riskv1decisionsOrderInformationLineItems.
        Per-item price of the product. This value for this field cannot be negative.  You must include either this field or the request-level field `orderInformation.amountDetails.totalAmount` in your request.  You can include a decimal point (.), but you cannot include any other special characters. The value is truncated to the correct number of decimal places.  #### DCC with a Third-Party Provider Set this field to the converted amount that was returned by the DCC provider. You must include either the 1st line item in the order and this field, or the request-level field `orderInformation.amountDetails.totalAmount` in your request.  #### FDMS South If you accept IDR or CLP currencies, see the entry for FDMS South in the [Merchant Descriptors Using the SCMP API Guide.] (https://apps.cybersource.com/library/documentation/dev_guides/Merchant_Descriptors_SCMP_API/html/)  #### Tax Calculation Required field for U.S., Canadian, international and value added taxes.  #### Zero Amount Authorizations If your processor supports zero amount authorizations, you can set this field to 0 for the authorization to check if the card is lost or stolen.  #### Maximum Field Lengths For GPN and JCN Gateway: Decimal (10) All other processors: Decimal (15) 

        :return: The unit_price of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._unit_price

    @unit_price.setter
    def unit_price(self, unit_price):
        """
        Sets the unit_price of this Riskv1decisionsOrderInformationLineItems.
        Per-item price of the product. This value for this field cannot be negative.  You must include either this field or the request-level field `orderInformation.amountDetails.totalAmount` in your request.  You can include a decimal point (.), but you cannot include any other special characters. The value is truncated to the correct number of decimal places.  #### DCC with a Third-Party Provider Set this field to the converted amount that was returned by the DCC provider. You must include either the 1st line item in the order and this field, or the request-level field `orderInformation.amountDetails.totalAmount` in your request.  #### FDMS South If you accept IDR or CLP currencies, see the entry for FDMS South in the [Merchant Descriptors Using the SCMP API Guide.] (https://apps.cybersource.com/library/documentation/dev_guides/Merchant_Descriptors_SCMP_API/html/)  #### Tax Calculation Required field for U.S., Canadian, international and value added taxes.  #### Zero Amount Authorizations If your processor supports zero amount authorizations, you can set this field to 0 for the authorization to check if the card is lost or stolen.  #### Maximum Field Lengths For GPN and JCN Gateway: Decimal (10) All other processors: Decimal (15) 

        :param unit_price: The unit_price of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._unit_price = unit_price

    @property
    def quantity(self):
        """
        Gets the quantity of this Riskv1decisionsOrderInformationLineItems.
        Number of units for this order. Must be a non-negative integer.  The default is `1`. For an authorization or capture transaction (`processingOptions.capture` is set to `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not `default` or one of the other values related to shipping and/or handling.  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes. 

        :return: The quantity of this Riskv1decisionsOrderInformationLineItems.
        :rtype: int
        """
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        """
        Sets the quantity of this Riskv1decisionsOrderInformationLineItems.
        Number of units for this order. Must be a non-negative integer.  The default is `1`. For an authorization or capture transaction (`processingOptions.capture` is set to `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not `default` or one of the other values related to shipping and/or handling.  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes. 

        :param quantity: The quantity of this Riskv1decisionsOrderInformationLineItems.
        :type: int
        """
        if quantity is not None and quantity > 999999999:
            raise ValueError("Invalid value for `quantity`, must be a value less than or equal to `999999999`")
        if quantity is not None and quantity < 1:
            raise ValueError("Invalid value for `quantity`, must be a value greater than or equal to `1`")

        self._quantity = quantity

    @property
    def gift_card_currency(self):
        """
        Gets the gift_card_currency of this Riskv1decisionsOrderInformationLineItems.
        When `orderInformation.lineItems[].productCode` is \"gift_card\", this is the currency used for the gift card purchase.  For details, see `pa_gift_card_currency` field description in [CyberSource Payer Authentication Using the SCMP API.] (https://apps.cybersource.com/library/documentation/dev_guides/Payer_Authentication_SCMP_API/Payer_Authentication_SCMP_API.pdf)  For the possible values, see the [ISO Standard Currency Codes.](http://apps.cybersource.com/library/documentation/sbc/quickref/currencies.pdf) 

        :return: The gift_card_currency of this Riskv1decisionsOrderInformationLineItems.
        :rtype: int
        """
        return self._gift_card_currency

    @gift_card_currency.setter
    def gift_card_currency(self, gift_card_currency):
        """
        Sets the gift_card_currency of this Riskv1decisionsOrderInformationLineItems.
        When `orderInformation.lineItems[].productCode` is \"gift_card\", this is the currency used for the gift card purchase.  For details, see `pa_gift_card_currency` field description in [CyberSource Payer Authentication Using the SCMP API.] (https://apps.cybersource.com/library/documentation/dev_guides/Payer_Authentication_SCMP_API/Payer_Authentication_SCMP_API.pdf)  For the possible values, see the [ISO Standard Currency Codes.](http://apps.cybersource.com/library/documentation/sbc/quickref/currencies.pdf) 

        :param gift_card_currency: The gift_card_currency of this Riskv1decisionsOrderInformationLineItems.
        :type: int
        """

        self._gift_card_currency = gift_card_currency

    @property
    def product_sku(self):
        """
        Gets the product_sku of this Riskv1decisionsOrderInformationLineItems.
        Product identifier code. Also known as the Stock Keeping Unit (SKU) code for the product.  For an authorization or capture transaction (`processingOptions.capture` is set to `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not set to **default** or one of the other values that are related to shipping and/or handling.  #### Tax Calculation Optional field for U.S. and Canadian taxes. Not applicable to international and value added taxes. For an authorization or capture transaction (`processingOptions.capture` is set to `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not `default` or one of the values related to shipping and/or handling. 

        :return: The product_sku of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._product_sku

    @product_sku.setter
    def product_sku(self, product_sku):
        """
        Sets the product_sku of this Riskv1decisionsOrderInformationLineItems.
        Product identifier code. Also known as the Stock Keeping Unit (SKU) code for the product.  For an authorization or capture transaction (`processingOptions.capture` is set to `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not set to **default** or one of the other values that are related to shipping and/or handling.  #### Tax Calculation Optional field for U.S. and Canadian taxes. Not applicable to international and value added taxes. For an authorization or capture transaction (`processingOptions.capture` is set to `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not `default` or one of the values related to shipping and/or handling. 

        :param product_sku: The product_sku of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._product_sku = product_sku

    @property
    def product_risk(self):
        """
        Gets the product_risk of this Riskv1decisionsOrderInformationLineItems.
        Indicates the level of risk for the product. This field can contain one of the following values: - `low`: The product is associated with few chargebacks. - `normal`: The product is associated with a normal number of chargebacks. - `high`: The product is associated with many chargebacks. 

        :return: The product_risk of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._product_risk

    @product_risk.setter
    def product_risk(self, product_risk):
        """
        Sets the product_risk of this Riskv1decisionsOrderInformationLineItems.
        Indicates the level of risk for the product. This field can contain one of the following values: - `low`: The product is associated with few chargebacks. - `normal`: The product is associated with a normal number of chargebacks. - `high`: The product is associated with many chargebacks. 

        :param product_risk: The product_risk of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._product_risk = product_risk

    @property
    def product_description(self):
        """
        Gets the product_description of this Riskv1decisionsOrderInformationLineItems.
        Brief description of item.

        :return: The product_description of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._product_description

    @product_description.setter
    def product_description(self, product_description):
        """
        Sets the product_description of this Riskv1decisionsOrderInformationLineItems.
        Brief description of item.

        :param product_description: The product_description of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._product_description = product_description

    @property
    def product_name(self):
        """
        Gets the product_name of this Riskv1decisionsOrderInformationLineItems.
        For an authorization or capture transaction (`processingOptions.capture` is `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not `default` or one of the other values that are related to shipping and/or handling.  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes. 

        :return: The product_name of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._product_name

    @product_name.setter
    def product_name(self, product_name):
        """
        Sets the product_name of this Riskv1decisionsOrderInformationLineItems.
        For an authorization or capture transaction (`processingOptions.capture` is `true` or `false`), this field is required when `orderInformation.lineItems[].productCode` is not `default` or one of the other values that are related to shipping and/or handling.  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes. 

        :param product_name: The product_name of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._product_name = product_name

    @property
    def product_code(self):
        """
        Gets the product_code of this Riskv1decisionsOrderInformationLineItems.
        Type of product. The value for this field is used to identify the product category (electronic, handling, physical, service, or shipping). The default value is `default`.  If you are performing an authorization transaction (`processingOptions.capture` is set to `false`), and you set this field to a value other than `default` or one of the values related to shipping and/or handling, then `orderInformation.lineItems[].quantity`, `orderInformation.lineItems[].productName`, and `orderInformation.lineItems[].productSku` fields are required.  Optional field.  For details, see the `product_code` field description in the [Credit Card Services Using the SCMP API Guide](https://apps.cybersource.com/library/documentation/dev_guides/CC_Svcs_SCMP_API/html/).  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes.  To use the tax calculation service, use values listed in the Tax Product Code Guide. For information about this document, contact customer support. See \"Product Codes,\" page 14, for more information. 

        :return: The product_code of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._product_code

    @product_code.setter
    def product_code(self, product_code):
        """
        Sets the product_code of this Riskv1decisionsOrderInformationLineItems.
        Type of product. The value for this field is used to identify the product category (electronic, handling, physical, service, or shipping). The default value is `default`.  If you are performing an authorization transaction (`processingOptions.capture` is set to `false`), and you set this field to a value other than `default` or one of the values related to shipping and/or handling, then `orderInformation.lineItems[].quantity`, `orderInformation.lineItems[].productName`, and `orderInformation.lineItems[].productSku` fields are required.  Optional field.  For details, see the `product_code` field description in the [Credit Card Services Using the SCMP API Guide](https://apps.cybersource.com/library/documentation/dev_guides/CC_Svcs_SCMP_API/html/).  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes.  To use the tax calculation service, use values listed in the Tax Product Code Guide. For information about this document, contact customer support. See \"Product Codes,\" page 14, for more information. 

        :param product_code: The product_code of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._product_code = product_code

    @property
    def gift(self):
        """
        Gets the gift of this Riskv1decisionsOrderInformationLineItems.
        This field is only used in DM service.  Determines whether to assign risk to the order if the billing and shipping addresses specify different cities, states, or countries. This field can contain one of the following values: - true: Orders are assigned only slight additional risk if billing and shipping addresses are different. - false: Orders are assigned higher additional risk if billing and shipping addresses are different. 

        :return: The gift of this Riskv1decisionsOrderInformationLineItems.
        :rtype: bool
        """
        return self._gift

    @gift.setter
    def gift(self, gift):
        """
        Sets the gift of this Riskv1decisionsOrderInformationLineItems.
        This field is only used in DM service.  Determines whether to assign risk to the order if the billing and shipping addresses specify different cities, states, or countries. This field can contain one of the following values: - true: Orders are assigned only slight additional risk if billing and shipping addresses are different. - false: Orders are assigned higher additional risk if billing and shipping addresses are different. 

        :param gift: The gift of this Riskv1decisionsOrderInformationLineItems.
        :type: bool
        """

        self._gift = gift

    @property
    def distributor_product_sku(self):
        """
        Gets the distributor_product_sku of this Riskv1decisionsOrderInformationLineItems.
        Product’s identifier code. This field is inserted into the outgoing message without being parsed or formatted. This field is included as Distributor product SKU (Offer) in the list of API fields with which you can create custom rules. 

        :return: The distributor_product_sku of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._distributor_product_sku

    @distributor_product_sku.setter
    def distributor_product_sku(self, distributor_product_sku):
        """
        Sets the distributor_product_sku of this Riskv1decisionsOrderInformationLineItems.
        Product’s identifier code. This field is inserted into the outgoing message without being parsed or formatted. This field is included as Distributor product SKU (Offer) in the list of API fields with which you can create custom rules. 

        :param distributor_product_sku: The distributor_product_sku of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._distributor_product_sku = distributor_product_sku

    @property
    def passenger(self):
        """
        Gets the passenger of this Riskv1decisionsOrderInformationLineItems.

        :return: The passenger of this Riskv1decisionsOrderInformationLineItems.
        :rtype: Ptsv2paymentsOrderInformationPassenger
        """
        return self._passenger

    @passenger.setter
    def passenger(self, passenger):
        """
        Sets the passenger of this Riskv1decisionsOrderInformationLineItems.

        :param passenger: The passenger of this Riskv1decisionsOrderInformationLineItems.
        :type: Ptsv2paymentsOrderInformationPassenger
        """

        self._passenger = passenger

    @property
    def shipping_destination_types(self):
        """
        Gets the shipping_destination_types of this Riskv1decisionsOrderInformationLineItems.
        Destination to where the item will be shipped. Example: Commercial, Residential, Store 

        :return: The shipping_destination_types of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._shipping_destination_types

    @shipping_destination_types.setter
    def shipping_destination_types(self, shipping_destination_types):
        """
        Sets the shipping_destination_types of this Riskv1decisionsOrderInformationLineItems.
        Destination to where the item will be shipped. Example: Commercial, Residential, Store 

        :param shipping_destination_types: The shipping_destination_types of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._shipping_destination_types = shipping_destination_types

    @property
    def tax_amount(self):
        """
        Gets the tax_amount of this Riskv1decisionsOrderInformationLineItems.
        Total tax to apply to the product. This value cannot be negative. The tax amount and the offer amount must be in the same currency. The tax amount field is additive.  The following example uses a two-exponent currency such as USD:   1. You include each line item in your request.  ..- 1st line item has amount=10.00, quantity=1, and taxAmount=0.80  ..- 2nd line item has amount=20.00, quantity=1, and taxAmount=1.60  2. The total amount authorized will be 32.40, not 30.00 with 2.40 of tax included.  Optional field.  #### Airlines processing Tax portion of the order amount. This value cannot exceed 99999999999999 (fourteen 9s). Format: English characters only. Optional request field for a line item.  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes.  Note if you send this field in your tax request, the value in the field will override the tax engine 

        :return: The tax_amount of this Riskv1decisionsOrderInformationLineItems.
        :rtype: str
        """
        return self._tax_amount

    @tax_amount.setter
    def tax_amount(self, tax_amount):
        """
        Sets the tax_amount of this Riskv1decisionsOrderInformationLineItems.
        Total tax to apply to the product. This value cannot be negative. The tax amount and the offer amount must be in the same currency. The tax amount field is additive.  The following example uses a two-exponent currency such as USD:   1. You include each line item in your request.  ..- 1st line item has amount=10.00, quantity=1, and taxAmount=0.80  ..- 2nd line item has amount=20.00, quantity=1, and taxAmount=1.60  2. The total amount authorized will be 32.40, not 30.00 with 2.40 of tax included.  Optional field.  #### Airlines processing Tax portion of the order amount. This value cannot exceed 99999999999999 (fourteen 9s). Format: English characters only. Optional request field for a line item.  #### Tax Calculation Optional field for U.S., Canadian, international tax, and value added taxes.  Note if you send this field in your tax request, the value in the field will override the tax engine 

        :param tax_amount: The tax_amount of this Riskv1decisionsOrderInformationLineItems.
        :type: str
        """

        self._tax_amount = tax_amount

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
        if not isinstance(other, Riskv1decisionsOrderInformationLineItems):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
