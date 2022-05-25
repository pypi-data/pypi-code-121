#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the objects to deserialize Connect public API Request objects
"""

from . import consts
from . import messages
from .exceptions import ConfigurationError


def to_dict(obj):
    """
    Nested object to dict
    """

    if not hasattr(obj, "__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        if isinstance(val, list):
            element = []
            for item in val:
                element.append(to_dict(item))
            result[key] = element
        else:
            result[key] = to_dict(val)
    return result


class Request:
    """
    Deserialization object for Request object of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)
        self.type = kwargs.get(consts.TYPE)
        self.note = kwargs.get(consts.NOTE)
        self.asset = Asset(**kwargs.get(consts.ASSET))
        self.reason = kwargs.get(consts.REASON)
        self.status = kwargs.get(consts.STATUS)
        self.created = kwargs.get(consts.CREATED)
        self.updated = kwargs.get(consts.UPDATED)
        self.answered = kwargs.get(consts.ANSWERED)
        self.assignee = kwargs.get(consts.ASSIGNEE)
        self.activation_key = kwargs.get(consts.ACTIVATION_KEY)
        self.previous_approved_request = kwargs.get(consts.PREVIOUS_APPROVED_REQUEST)
        self.effective_date = kwargs.get(consts.EFFECTIVE_DATE)
        self.planned_date = kwargs.get(consts.PLANNED_DATE)
        self.events = Events(**kwargs.get(consts.EVENTS))
        self.marketplace = Marketplace(**kwargs.get(consts.MARKETPLACE))
        self.contract = Named(**kwargs.get(consts.CONTRACT))

    def get_marketplace_id(self):
        return self.marketplace.id

    def get_asset(self):
        return self.asset

    def get_asset_id(self):
        return self.asset.id

    def get_asset_params(self):
        return self.asset.params

    def get_asset_configuration_params(self):
        return self.asset.configuration.params

    def get_items(self):
        return self.asset.items

    def get_product_id(self):
        return self.asset.product.id

    def get_asset_connection_type(self):
        return self.asset.connection.type

    def get_hub_id(self):
        return self.asset.connection.hub.id

    def get_customer_id(self):
        return self.asset.tiers.customer.id

    def get_customer_name(self):
        return self.asset.tiers.customer.name

    def get_customer_external_id(self):
        return self.asset.tiers.customer.external_id

    def get_customer_contact_first_name(self):
        return self.asset.tiers.customer.contact_info.contact.first_name

    def get_customer_contact_last_name(self):
        return self.asset.tiers.customer.contact_info.contact.last_name

    def get_customer_contact_email(self):
        return self.asset.tiers.customer.contact_info.contact.email


class Param:
    """
    Deserialization object for Param object of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)
        if consts.NAME in kwargs:
            self.name = kwargs.get(consts.NAME)
        self.type = kwargs.get(consts.TYPE)
        self.phase = kwargs.get(consts.PHASE)
        self.description = kwargs.get(consts.DESCRIPTION)
        self.value = kwargs.get(consts.VALUE)
        self.title = kwargs.get(consts.TITLE)
        self.constraints = Constraints(**kwargs.get(consts.CONSTRAINTS))
        if consts.VALUE_ERROR in kwargs:
            self.value_error = kwargs.get(consts.VALUE_ERROR)


class ConfigurationParam:
    """
    Deserialization object for Configuration Param object of Connect public API
    """

    def __init__(self, **kwargs):
        self.value = kwargs.get(consts.VALUE)
        self.events = Events(**kwargs.get(consts.EVENTS))
        self.id = kwargs.get(consts.ID)
        self.title = kwargs.get(consts.TITLE)
        self.description = kwargs.get(consts.DESCRIPTION)
        self.type = kwargs.get(consts.TYPE)
        self.scope = kwargs.get(consts.SCOPE)
        self.phase = kwargs.get(consts.PHASE)
        self.hint = kwargs.get(consts.HINT)
        if consts.PLACEHOLDER in kwargs:
            self.placeholder = kwargs.get(consts.PLACEHOLDER)
        self.constraints = Constraints(**kwargs.get(consts.CONSTRAINTS))


class ParamsManager:
    """
    Deserialization base class for params object of Connect public API
    """

    def __init__(self, params: list):
        self.params = params

    def update_parameter(self, param_id: str, value: str = '', value_error: str = None) -> dict:
        """
        Update parameter

        :param param_id: parameter identifier to be updated
        :param value: new value to parameter
        :param value_error: error associated to parameter -if case-

        :return: request data
        """

        param = self.search_param(param_id)
        if value:
            param.value = value
        if value_error is not None:
            param.value_error = value_error

        parameter = {consts.ID: param.id, consts.VALUE: param.value}
        if value_error is not None:
            parameter[consts.VALUE_ERROR] = value_error

        return parameter

    def search_param(self, param_id: str) -> Param:
        """
        Search for a parameter in the list by its id

        :param param_id: parameter identifier

        :return: Param

        :raises: ConfigurationError
        """

        try:
            return next(filter(lambda param: param.id == param_id, self.params))
        except StopIteration:
            raise ConfigurationError(messages.CONFIGURATION_ERROR_PARAMETER.format(id=param_id))

    def get_param_value(self, param_id: str) -> str:
        """
        Gets a parameter value by its id. Empty value, if no parameter or value.

        :param param_id: parameter identifier

        :return: parameter value
        """

        if not self.params:
            return ''
        param = self.search_param(param_id)
        return param.value if param else ''


class Configuration(ParamsManager):
    """
    Deserialization object for Configuration object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__([ConfigurationParam(**p) for p in kwargs.get(consts.PARAMS)])


class Item(ParamsManager):
    """
    Deserialization object for Item object of Connect public API
    """

    def __init__(self, **kwargs):
        if consts.PARAMS in kwargs:
            super().__init__([Param(**p) for p in kwargs.get(consts.PARAMS)])

        self.id = kwargs.get(consts.ID)
        self.global_id = kwargs.get(consts.GLOBAL_ID)
        self.mpn = kwargs.get(consts.MPN)
        self.old_quantity = int(kwargs.get(consts.OLD_QUANTITY))
        self.quantity = int(kwargs.get(consts.QUANTITY))
        self.type = kwargs.get(consts.TYPE)
        self.display_name = kwargs.get(consts.DISPLAY_NAME)
        self.period = kwargs.get(consts.PERIOD)
        self.item_type = kwargs.get(consts.ITEM_TYPE)


class Asset(ParamsManager):
    """
    Deserialization object for Asset object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__([Param(**p) for p in kwargs.get(consts.PARAMS)])

        self.id = kwargs.get(consts.ID)
        self.status = kwargs.get(consts.STATUS)
        self.external_id = kwargs.get(consts.EXTERNAL_ID)
        self.external_uid = kwargs.get(consts.EXTERNAL_UID)
        self.product = Product(**kwargs.get(consts.PRODUCT))
        self.connection = Connection(**kwargs.get(consts.CONNECTION))
        self.events = Events(**kwargs.get(consts.EVENTS))
        self.items = [Item(**item) for item in kwargs.get(consts.ITEMS)]
        self.tiers = Tiers(**kwargs.get(consts.TIERS))
        self.configuration = Configuration(**kwargs.get(consts.CONFIGURATION))
        self.marketplace = Marketplace(**kwargs.get(consts.MARKETPLACE))
        self.contract = Named(**kwargs.get(consts.CONTRACT))


class Tiers:
    """
    Deserialization object for Tiers object of Connect public API
    """

    def __init__(self, **kwargs):
        self.customer = Tier(**kwargs.get(consts.CUSTOMER))
        self.tier1 = Tier(**kwargs.get(consts.TIER1))
        self.tier2 = Tier(**kwargs.get(consts.TIER2))


class Tier:
    """
    Deserialization object for Tier object of Connect public API
    """

    def __init__(self, **kwargs):
        if consts.ID in kwargs:
            self.id = kwargs.get(consts.ID)
        if consts.VERSION in kwargs:
            self.version = kwargs.get(consts.VERSION)
        if consts.NAME in kwargs:
            self.name = kwargs.get(consts.NAME)
        if consts.TYPE in kwargs:
            self.type = kwargs.get(consts.TYPE)
        if consts.EXTERNAL_ID in kwargs:
            self.external_id = kwargs.get(consts.EXTERNAL_ID)
        if consts.EXTERNAL_UID in kwargs:
            self.external_uid = kwargs.get(consts.EXTERNAL_UID)
        if consts.PARENT in kwargs:
            self.parent = Parent(**kwargs.get(consts.PARENT))
        if consts.OWNER in kwargs:
            self.owner = Named(**kwargs.get(consts.OWNER))
        if consts.SCOPES in kwargs:
            self.scopes = kwargs.get(consts.SCOPES)
        if consts.HUB in kwargs:
            self.hub = Named(**kwargs.get(consts.HUB))
        if consts.TAX_ID in kwargs:
            self.tax_id = kwargs.get(consts.TAX_ID)
        if consts.EVENTS in kwargs:
            self.events = Events(**kwargs.get(consts.EVENTS))
        if consts.CONTACT_INFO in kwargs:
            self.contact_info = ContactInfo(**kwargs.get(consts.CONTACT_INFO))


class ContactInfo:
    """
    Deserialization object for ContactInfo object of Connect public API
    """

    def __init__(self, **kwargs):
        self.address_line1 = kwargs.get(consts.ADDRESS_LINE1)
        self.address_line2 = kwargs.get(consts.ADDRESS_LINE2)
        self.city = kwargs.get(consts.CITY)
        self.state = kwargs.get(consts.STATE)
        self.postal_code = kwargs.get(consts.POSTAL_CODE)
        self.country = kwargs.get(consts.COUNTRY)
        self.contact = Contact(**kwargs.get(consts.CONTACT))


class Contact:
    """
    Deserialization object for Contact object of Connect public API
    """

    def __init__(self, **kwargs):
        self.first_name = kwargs.get(consts.FIRST_NAME)
        self.last_name = kwargs.get(consts.LAST_NAME)
        self.email = kwargs.get(consts.EMAIL)
        self.phone_number = PhoneNumber(**kwargs.get(consts.PHONE_NUMBER))


class PhoneNumber:
    """
    Deserialization object for PhoneNumber object of Connect public API
    """

    def __init__(self, **kwargs):
        self.country_code = kwargs.get(consts.COUNTRY_CODE)
        self.area_code = kwargs.get(consts.AREA_CODE)
        self.phone_number = kwargs.get(consts.PHONE_NUMBER)
        self.extension = kwargs.get(consts.EXTENSION)


class Named:
    """
    Deserialization object for Named objects of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)
        self.name = kwargs.get(consts.NAME)


class Parent(Named):
    """
    Deserialization object for Parent object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.external_id = kwargs.get(consts.EXTERNAL_ID)


class Events:
    """
    Deserialization object for Events object of Connect public API
    """

    def __init__(self, **kwargs):
        self.created = Dated(**kwargs.get(consts.CREATED))
        self.updated = Dated(**kwargs.get(consts.UPDATED))


class Dated:
    """
    Deserialization object for Dated object of Connect public API
    """

    def __init__(self, **kwargs):
        self.at = kwargs.get(consts.AT)
        if consts.BY in kwargs:
            self.by = Named(**kwargs.get(consts.BY))


class Marketplace(Named):
    """
    Deserialization object for Marketplace object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = kwargs.get(consts.ICON)


class Product(Named):
    """
    Deserialization object for Product object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = kwargs.get(consts.ICON)
        self.status = kwargs.get(consts.STATUS)


class Constraints:
    """
    Deserialization object for Constraints object of Connect public API
    """

    def __init__(self, **kwargs):
        self.required = kwargs.get(consts.REQUIRED)
        if consts.META in kwargs:
            self.meta = kwargs.get(consts.META)
        if consts.MAX_LENGTH in kwargs:
            self.max_length = kwargs.get(consts.MAX_LENGTH)
        if consts.MIN_LENGTH in kwargs:
            self.min_length = kwargs.get(consts.MIN_LENGTH)
        if consts.HIDDEN in kwargs:
            self.hidden = kwargs.get(consts.HIDDEN)
        if consts.UNIQUE in kwargs:
            self.unique = kwargs.get(consts.UNIQUE)
        if consts.PLACEHOLDER in kwargs:
            self.placeholder = kwargs.get(consts.PLACEHOLDER)
        if consts.RECONCILIATION in kwargs:
            self.reconciliation = kwargs.get(consts.RECONCILIATION)
        if consts.HINT in kwargs:
            self.hint = kwargs.get(consts.HINT)
        if consts.SHARED in kwargs:
            self.shared = kwargs.get(consts.SHARED)


class Connection:
    """
    Deserialization object for Connection object of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)
        self.type = kwargs.get(consts.TYPE)
        self.provider = Named(**kwargs.get(consts.PROVIDER))
        self.vendor = Named(**kwargs.get(consts.VENDOR))
        self.hub = Named(**kwargs.get(consts.HUB))
