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


class Ptsv2paymentsPointOfSaleInformationEmv(object):
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
        'tags': 'str',
        'cardholder_verification_method_used': 'int',
        'card_sequence_number': 'str',
        'fallback': 'bool',
        'fallback_condition': 'int',
        'is_repeat': 'str'
    }

    attribute_map = {
        'tags': 'tags',
        'cardholder_verification_method_used': 'cardholderVerificationMethodUsed',
        'card_sequence_number': 'cardSequenceNumber',
        'fallback': 'fallback',
        'fallback_condition': 'fallbackCondition',
        'is_repeat': 'isRepeat'
    }

    def __init__(self, tags=None, cardholder_verification_method_used=None, card_sequence_number=None, fallback=None, fallback_condition=None, is_repeat=None):
        """
        Ptsv2paymentsPointOfSaleInformationEmv - a model defined in Swagger
        """

        self._tags = None
        self._cardholder_verification_method_used = None
        self._card_sequence_number = None
        self._fallback = None
        self._fallback_condition = None
        self._is_repeat = None

        if tags is not None:
          self.tags = tags
        if cardholder_verification_method_used is not None:
          self.cardholder_verification_method_used = cardholder_verification_method_used
        if card_sequence_number is not None:
          self.card_sequence_number = card_sequence_number
        if fallback is not None:
          self.fallback = fallback
        if fallback_condition is not None:
          self.fallback_condition = fallback_condition
        if is_repeat is not None:
          self.is_repeat = is_repeat

    @property
    def tags(self):
        """
        Gets the tags of this Ptsv2paymentsPointOfSaleInformationEmv.
        EMV data that is transmitted from the chip card to the issuer, and from the issuer to the chip card. The EMV data is in the tag-length-value format and includes chip card tags, terminal tags, and transaction detail tags.  For information about the individual tags, see the “Application Specification” section in the EMV 4.3 Specifications: http://emvco.com  **Note** Card present information about EMV applies only to credit card processing and PIN debit processing. All other card present information applies only to credit card processing. PIN debit processing is available only on FDC Nashville Global.  **Important** The following tags contain sensitive information and **must not** be included in this field:   - `56`: Track 1 equivalent data  - `57`: Track 2 equivalent data  - `5A`: Application PAN  - `5F20`: Cardholder name  - `5F24`: Application expiration date (This sensitivity has been relaxed for Credit Mutuel-CIC, American Express Direct, FDC Nashville Global, First Data Merchant Solutions, and SIX)  - `99`: Transaction PIN  - `9F0B`: Cardholder name (extended)  - `9F1F`: Track 1 discretionary data  - `9F20`: Track 2 discretionary data  For captures, this field is required for contact EMV transactions. Otherwise, it is optional.  For credits, this field is required for contact EMV stand-alone credits and contactless EMV stand-alone credits. Otherwise, it is optional.  **Important** For contact EMV captures, contact EMV stand-alone credits, and contactless EMV stand-alone credits, you must include the following tags in this field. For all other types of EMV transactions, the following tags are optional.   - `95`: Terminal verification results  - `9F10`: Issuer application data  - `9F26`: Application cryptogram   #### CyberSource through VisaNet - In Japan: 199 bytes - In other countries: String (252)  #### GPX This field only supports transactions from the following card types: - Visa - Mastercard - AMEX - Discover - Diners - JCB - Union Pay International  #### JCN Gateway The following tags must be included: - `4F`: Application identifier - `84`: Dedicated file name  Data length: 199 bytes  #### All other processors: String (999)  #### Used by Authorization: Optional Authorization Reversal: Optional Credit: Optional PIN Debit processing (purchase, credit and reversal): Optional 

        :return: The tags of this Ptsv2paymentsPointOfSaleInformationEmv.
        :rtype: str
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """
        Sets the tags of this Ptsv2paymentsPointOfSaleInformationEmv.
        EMV data that is transmitted from the chip card to the issuer, and from the issuer to the chip card. The EMV data is in the tag-length-value format and includes chip card tags, terminal tags, and transaction detail tags.  For information about the individual tags, see the “Application Specification” section in the EMV 4.3 Specifications: http://emvco.com  **Note** Card present information about EMV applies only to credit card processing and PIN debit processing. All other card present information applies only to credit card processing. PIN debit processing is available only on FDC Nashville Global.  **Important** The following tags contain sensitive information and **must not** be included in this field:   - `56`: Track 1 equivalent data  - `57`: Track 2 equivalent data  - `5A`: Application PAN  - `5F20`: Cardholder name  - `5F24`: Application expiration date (This sensitivity has been relaxed for Credit Mutuel-CIC, American Express Direct, FDC Nashville Global, First Data Merchant Solutions, and SIX)  - `99`: Transaction PIN  - `9F0B`: Cardholder name (extended)  - `9F1F`: Track 1 discretionary data  - `9F20`: Track 2 discretionary data  For captures, this field is required for contact EMV transactions. Otherwise, it is optional.  For credits, this field is required for contact EMV stand-alone credits and contactless EMV stand-alone credits. Otherwise, it is optional.  **Important** For contact EMV captures, contact EMV stand-alone credits, and contactless EMV stand-alone credits, you must include the following tags in this field. For all other types of EMV transactions, the following tags are optional.   - `95`: Terminal verification results  - `9F10`: Issuer application data  - `9F26`: Application cryptogram   #### CyberSource through VisaNet - In Japan: 199 bytes - In other countries: String (252)  #### GPX This field only supports transactions from the following card types: - Visa - Mastercard - AMEX - Discover - Diners - JCB - Union Pay International  #### JCN Gateway The following tags must be included: - `4F`: Application identifier - `84`: Dedicated file name  Data length: 199 bytes  #### All other processors: String (999)  #### Used by Authorization: Optional Authorization Reversal: Optional Credit: Optional PIN Debit processing (purchase, credit and reversal): Optional 

        :param tags: The tags of this Ptsv2paymentsPointOfSaleInformationEmv.
        :type: str
        """

        self._tags = tags

    @property
    def cardholder_verification_method_used(self):
        """
        Gets the cardholder_verification_method_used of this Ptsv2paymentsPointOfSaleInformationEmv.
        Method that was used to verify the cardholder's identity.  Possible values:  - `0`: No verification  - `1`: Signature  This field is supported only on **American Express Direct**. 

        :return: The cardholder_verification_method_used of this Ptsv2paymentsPointOfSaleInformationEmv.
        :rtype: int
        """
        return self._cardholder_verification_method_used

    @cardholder_verification_method_used.setter
    def cardholder_verification_method_used(self, cardholder_verification_method_used):
        """
        Sets the cardholder_verification_method_used of this Ptsv2paymentsPointOfSaleInformationEmv.
        Method that was used to verify the cardholder's identity.  Possible values:  - `0`: No verification  - `1`: Signature  This field is supported only on **American Express Direct**. 

        :param cardholder_verification_method_used: The cardholder_verification_method_used of this Ptsv2paymentsPointOfSaleInformationEmv.
        :type: int
        """

        self._cardholder_verification_method_used = cardholder_verification_method_used

    @property
    def card_sequence_number(self):
        """
        Gets the card_sequence_number of this Ptsv2paymentsPointOfSaleInformationEmv.
        Number assigned to a specific card when two or more cards are associated with the same primary account number. This value enables issuers to distinguish among multiple cards that are linked to the same account. This value can also act as a tracking tool when reissuing cards. When this value is available, it is provided by the chip reader. When the chip reader does not provide this value, do not include this field in your request.  **Note** Card present information about EMV applies only to credit card processing and PIN debit processing. All other card present information applies only to credit card processing. PIN debit processing is available only on CyberSource through VisaNet and FDC Nashville Global.  #### Used by Authorization: Optional PIN Debit processing: Optional  #### GPX  This field only supports transactions from the following card types: - Visa - Mastercard - AMEX - Discover - Diners - JCB - Union Pay International 

        :return: The card_sequence_number of this Ptsv2paymentsPointOfSaleInformationEmv.
        :rtype: str
        """
        return self._card_sequence_number

    @card_sequence_number.setter
    def card_sequence_number(self, card_sequence_number):
        """
        Sets the card_sequence_number of this Ptsv2paymentsPointOfSaleInformationEmv.
        Number assigned to a specific card when two or more cards are associated with the same primary account number. This value enables issuers to distinguish among multiple cards that are linked to the same account. This value can also act as a tracking tool when reissuing cards. When this value is available, it is provided by the chip reader. When the chip reader does not provide this value, do not include this field in your request.  **Note** Card present information about EMV applies only to credit card processing and PIN debit processing. All other card present information applies only to credit card processing. PIN debit processing is available only on CyberSource through VisaNet and FDC Nashville Global.  #### Used by Authorization: Optional PIN Debit processing: Optional  #### GPX  This field only supports transactions from the following card types: - Visa - Mastercard - AMEX - Discover - Diners - JCB - Union Pay International 

        :param card_sequence_number: The card_sequence_number of this Ptsv2paymentsPointOfSaleInformationEmv.
        :type: str
        """

        self._card_sequence_number = card_sequence_number

    @property
    def fallback(self):
        """
        Gets the fallback of this Ptsv2paymentsPointOfSaleInformationEmv.
        Indicates whether a fallback method was used to enter credit card information into the POS terminal. When a technical problem prevents a successful exchange of information between a chip card and a chip-capable terminal:   1. Swipe the card or key the credit card information into the POS terminal.  2. Use the pointOfSaleInformation.entryMode field to indicate whether the information was swiped or keyed.   Possible values: - `true`: Fallback method was used. - `false` (default): Fallback method was not used.  This field is supported only on American Express Direct, Chase Paymentech Solutions, CyberSource through VisaNet, FDC Nashville Global, GPN, JCN Gateway, OmniPay Direct, and SIX. 

        :return: The fallback of this Ptsv2paymentsPointOfSaleInformationEmv.
        :rtype: bool
        """
        return self._fallback

    @fallback.setter
    def fallback(self, fallback):
        """
        Sets the fallback of this Ptsv2paymentsPointOfSaleInformationEmv.
        Indicates whether a fallback method was used to enter credit card information into the POS terminal. When a technical problem prevents a successful exchange of information between a chip card and a chip-capable terminal:   1. Swipe the card or key the credit card information into the POS terminal.  2. Use the pointOfSaleInformation.entryMode field to indicate whether the information was swiped or keyed.   Possible values: - `true`: Fallback method was used. - `false` (default): Fallback method was not used.  This field is supported only on American Express Direct, Chase Paymentech Solutions, CyberSource through VisaNet, FDC Nashville Global, GPN, JCN Gateway, OmniPay Direct, and SIX. 

        :param fallback: The fallback of this Ptsv2paymentsPointOfSaleInformationEmv.
        :type: bool
        """

        self._fallback = fallback

    @property
    def fallback_condition(self):
        """
        Gets the fallback_condition of this Ptsv2paymentsPointOfSaleInformationEmv.
        Reason for the EMV fallback transaction. An EMV fallback transaction occurs when an EMV transaction fails for one of these reasons:   - Technical failure: the EMV terminal or EMV card cannot read and process chip data.  - Empty candidate list failure: the EMV terminal does not have any applications in common with the EMV card.    EMV terminals are coded to determine whether the terminal and EMV card have any applications in common.    EMV terminals provide this information to you.  Possible values:   - `1`: Transaction was initiated with information from a magnetic stripe, and the previous transaction at the     EMV terminal either used information from a successful chip read or it was not a chip transaction.  - `2`: Transaction was initiated with information from a magnetic stripe, and the previous transaction at the     EMV terminal was an EMV fallback transaction because the attempted chip read was unsuccessful.  This field is supported only on **GPN** and **JCN Gateway**. **NOTE**: This field is required when an EMV transaction fails for a technical reason. Do not include this field when the EMV terminal does not have any applications in common with the EMV card. 

        :return: The fallback_condition of this Ptsv2paymentsPointOfSaleInformationEmv.
        :rtype: int
        """
        return self._fallback_condition

    @fallback_condition.setter
    def fallback_condition(self, fallback_condition):
        """
        Sets the fallback_condition of this Ptsv2paymentsPointOfSaleInformationEmv.
        Reason for the EMV fallback transaction. An EMV fallback transaction occurs when an EMV transaction fails for one of these reasons:   - Technical failure: the EMV terminal or EMV card cannot read and process chip data.  - Empty candidate list failure: the EMV terminal does not have any applications in common with the EMV card.    EMV terminals are coded to determine whether the terminal and EMV card have any applications in common.    EMV terminals provide this information to you.  Possible values:   - `1`: Transaction was initiated with information from a magnetic stripe, and the previous transaction at the     EMV terminal either used information from a successful chip read or it was not a chip transaction.  - `2`: Transaction was initiated with information from a magnetic stripe, and the previous transaction at the     EMV terminal was an EMV fallback transaction because the attempted chip read was unsuccessful.  This field is supported only on **GPN** and **JCN Gateway**. **NOTE**: This field is required when an EMV transaction fails for a technical reason. Do not include this field when the EMV terminal does not have any applications in common with the EMV card. 

        :param fallback_condition: The fallback_condition of this Ptsv2paymentsPointOfSaleInformationEmv.
        :type: int
        """

        self._fallback_condition = fallback_condition

    @property
    def is_repeat(self):
        """
        Gets the is_repeat of this Ptsv2paymentsPointOfSaleInformationEmv.
        #### Visa Platform Connect Value 1  indicates this transaction is intentionally duplicated  The field contains value “1” which indicates that merchant has intentionally duplicated single tap transaction. Merchant is intentionally sending a duplicate auth request for a single tap txn because the issuer requested a PIN. 

        :return: The is_repeat of this Ptsv2paymentsPointOfSaleInformationEmv.
        :rtype: str
        """
        return self._is_repeat

    @is_repeat.setter
    def is_repeat(self, is_repeat):
        """
        Sets the is_repeat of this Ptsv2paymentsPointOfSaleInformationEmv.
        #### Visa Platform Connect Value 1  indicates this transaction is intentionally duplicated  The field contains value “1” which indicates that merchant has intentionally duplicated single tap transaction. Merchant is intentionally sending a duplicate auth request for a single tap txn because the issuer requested a PIN. 

        :param is_repeat: The is_repeat of this Ptsv2paymentsPointOfSaleInformationEmv.
        :type: str
        """

        self._is_repeat = is_repeat

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
        if not isinstance(other, Ptsv2paymentsPointOfSaleInformationEmv):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
