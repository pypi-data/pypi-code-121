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
        self.asset = Asset(**kwargs.get(consts.ASSET))
        self.status = kwargs.get(consts.STATUS)

        # Validate fields before taking values
        if consts.TYPE in kwargs:
            self.type = kwargs.get(consts.TYPE)
        if consts.NOTE in kwargs:
            self.note = kwargs.get(consts.NOTE)
        if consts.REASON in kwargs:
            self.reason = kwargs.get(consts.REASON)
        if consts.CREATED in kwargs:
            self.created = kwargs.get(consts.CREATED)
        if consts.UPDATED in kwargs:
            self.updated = kwargs.get(consts.UPDATED)
        if consts.ANSWERED in kwargs:
            self.answered = kwargs.get(consts.ANSWERED)
        if consts.ASSIGNEE in kwargs:
            self.assignee = kwargs.get(consts.ASSIGNEE)
        if consts.ACTIVATION_KEY in kwargs:
            self.activation_key = kwargs.get(consts.ACTIVATION_KEY)
        if consts.PREVIOUS_APPROVED_REQUEST in kwargs:
            self.previous_approved_request = kwargs.get(consts.PREVIOUS_APPROVED_REQUEST)
        if consts.EFFECTIVE_DATE in kwargs:
            self.effective_date = kwargs.get(consts.EFFECTIVE_DATE)
        if consts.PLANNED_DATE in kwargs:
            self.planned_date = kwargs.get(consts.PLANNED_DATE)
        if consts.EVENTS in kwargs:
            self.events = Events(**kwargs.get(consts.EVENTS))
        if consts.MARKETPLACE in kwargs:
            self.marketplace = Marketplace(**kwargs.get(consts.MARKETPLACE))
        if consts.CONTRACT in kwargs:
            self.contract = Named(**kwargs.get(consts.CONTRACT))

    # Accessory methods
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

        # Validate fields before taking values
        if consts.NAME in kwargs:
            self.name = kwargs.get(consts.NAME)
        if consts.TYPE in kwargs:
            self.type = kwargs.get(consts.TYPE)
        if consts.PHASE in kwargs:
            self.phase = kwargs.get(consts.PHASE)
        if consts.DESCRIPTION in kwargs:
            self.description = kwargs.get(consts.DESCRIPTION)
        if consts.VALUE in kwargs:
            self.value = kwargs.get(consts.VALUE)
        if consts.TITLE in kwargs:
            self.title = kwargs.get(consts.TITLE)
        if consts.CONSTRAINTS in kwargs:
            self.constraints = Constraints(**kwargs.get(consts.CONSTRAINTS))
        if consts.VALUE_ERROR in kwargs:
            self.value_error = kwargs.get(consts.VALUE_ERROR)


class ConfigurationParam:
    """
    Deserialization object for Configuration Param object of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)

        # Validate fields before taking values
        if consts.VALUE in kwargs:
            self.value = kwargs.get(consts.VALUE)
        if consts.EVENTS in kwargs:
            self.events = Events(**kwargs.get(consts.EVENTS))
        if consts.TITLE in kwargs:
            self.title = kwargs.get(consts.TITLE)
        if consts.DESCRIPTION in kwargs:
            self.description = kwargs.get(consts.DESCRIPTION)
        if consts.TYPE in kwargs:
            self.type = kwargs.get(consts.TYPE)
        if consts.SCOPE in kwargs:
            self.scope = kwargs.get(consts.SCOPE)
        if consts.PHASE in kwargs:
            self.phase = kwargs.get(consts.PHASE)
        if consts.HINT in kwargs:
            self.hint = kwargs.get(consts.HINT)
        if consts.PLACEHOLDER in kwargs:
            self.placeholder = kwargs.get(consts.PLACEHOLDER)
        if consts.CONSTRAINTS in kwargs:
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
        if consts.PARAMS in kwargs:
            super().__init__([ConfigurationParam(**p) for p in kwargs.get(consts.PARAMS)])


class Item(ParamsManager):
    """
    Deserialization object for Item object of Connect public API
    """

    def __init__(self, **kwargs):
        if consts.PARAMS in kwargs:
            super().__init__([Param(**p) for p in kwargs.get(consts.PARAMS)])

        self.id = kwargs.get(consts.ID)

        # Validate fields before taking values
        if consts.GLOBAL_ID in kwargs:
            self.GLOBAL_ID = kwargs.get(consts.GLOBAL_ID)
        if consts.MPN in kwargs:
            self.mpn = kwargs.get(consts.MPN)
        if consts.OLD_QUANTITY in kwargs:
            self.old_quantity = int(kwargs.get(consts.OLD_QUANTITY))
        if consts.QUANTITY in kwargs:
            self.quantity = int(kwargs.get(consts.QUANTITY))
        if consts.TYPE in kwargs:
            self.type = kwargs.get(consts.TYPE)
        if consts.DISPLAY_NAME in kwargs:
            self.display_name = kwargs.get(consts.DISPLAY_NAME)
        if consts.PERIOD in kwargs:
            self.period = kwargs.get(consts.PERIOD)
        if consts.ITEM_TYPE in kwargs:
            self.item_type = kwargs.get(consts.ITEM_TYPE)


class Asset(ParamsManager):
    """
    Deserialization object for Asset object of Connect public API
    """

    def __init__(self, **kwargs):
        if consts.PARAMS in kwargs:
            super().__init__([Param(**p) for p in kwargs.get(consts.PARAMS)])

        self.id = kwargs.get(consts.ID)

        # Validate fields before taking values
        if consts.STATUS in kwargs:
            self.status = kwargs.get(consts.STATUS)
        if consts.EXTERNAL_ID in kwargs:
            self.external_id = kwargs.get(consts.EXTERNAL_ID)
        if consts.EXTERNAL_UID in kwargs:
            self.external_uid = kwargs.get(consts.EXTERNAL_UID)
        if consts.PRODUCT in kwargs:
            self.product = Product(**kwargs.get(consts.PRODUCT))
        if consts.CONNECTION in kwargs:
            self.connection = Connection(**kwargs.get(consts.CONNECTION))
        if consts.EVENTS in kwargs:
            self.events = Events(**kwargs.get(consts.EVENTS))
        if consts.ITEMS in kwargs:
            self.items = [Item(**item) for item in kwargs.get(consts.ITEMS)]
        if consts.TIERS in kwargs:
            self.tiers = Tiers(**kwargs.get(consts.TIERS))
        if consts.CONFIGURATION in kwargs:
            self.configuration = Configuration(**kwargs.get(consts.CONFIGURATION))
        if consts.MARKETPLACE in kwargs:
            self.marketplace = Marketplace(**kwargs.get(consts.MARKETPLACE))
        if consts.CONTRACT in kwargs:
            self.contract = Named(**kwargs.get(consts.CONTRACT))


class Tiers:
    """
    Deserialization object for Tiers object of Connect public API
    """

    def __init__(self, **kwargs):
        # Validate fields before taking values
        if consts.CUSTOMER in kwargs:
            self.customer = Tier(**kwargs.get(consts.CUSTOMER))
        if consts.TIER1 in kwargs:
            self.tier1 = Tier(**kwargs.get(consts.TIER1))
        if consts.TIER2 in kwargs:
            self.tier2 = Tier(**kwargs.get(consts.TIER2))


class Tier:
    """
    Deserialization object for Tier object of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)

        # Validate fields before taking values
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
        # Validate fields before taking values
        if consts.ADDRESS_LINE1 in kwargs:
            self.address_line1 = kwargs.get(consts.ADDRESS_LINE1)
        if consts.ADDRESS_LINE2 in kwargs:
            self.address_line2 = kwargs.get(consts.ADDRESS_LINE2)
        if consts.CITY in kwargs:
            self.city = kwargs.get(consts.CITY)
        if consts.STATE in kwargs:
            self.state = kwargs.get(consts.STATE)
        if consts.POSTAL_CODE in kwargs:
            self.postal_code = kwargs.get(consts.POSTAL_CODE)
        if consts.COUNTRY in kwargs:
            self.country = kwargs.get(consts.COUNTRY)
        if consts.CONTACT in kwargs:
            self.contact = Contact(**kwargs.get(consts.CONTACT))


class Contact:
    """
    Deserialization object for Contact object of Connect public API
    """

    def __init__(self, **kwargs):
        # Validate fields before taking values
        if consts.FIRST_NAME in kwargs:
            self.first_name = kwargs.get(consts.FIRST_NAME)
        if consts.LAST_NAME in kwargs:
            self.last_name = kwargs.get(consts.LAST_NAME)
        if consts.EMAIL in kwargs:
            self.email = kwargs.get(consts.EMAIL)
        if consts.PHONE_NUMBER in kwargs:
            self.phone_number = PhoneNumber(**kwargs.get(consts.PHONE_NUMBER))


class PhoneNumber:
    """
    Deserialization object for PhoneNumber object of Connect public API
    """

    def __init__(self, **kwargs):
        # Validate fields before taking values
        if consts.COUNTRY_CODE in kwargs:
            self.country_code = kwargs.get(consts.COUNTRY_CODE)
        if consts.AREA_CODE in kwargs:
            self.area_code = kwargs.get(consts.AREA_CODE)
        if consts.PHONE_NUMBER in kwargs:
            self.phone_number = kwargs.get(consts.PHONE_NUMBER)
        if consts.EXTENSION in kwargs:
            self.extension = kwargs.get(consts.EXTENSION)


class Named:
    """
    Deserialization object for Named objects of Connect public API
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get(consts.ID)

        # Validate fields before taking values
        if consts.NAME in kwargs:
            self.name = kwargs.get(consts.NAME)


class Parent(Named):
    """
    Deserialization object for Parent object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Validate fields before taking values
        if consts.EXTERNAL_ID in kwargs:
            self.external_id = kwargs.get(consts.EXTERNAL_ID)


class Events:
    """
    Deserialization object for Events object of Connect public API
    """

    def __init__(self, **kwargs):
        # Validate fields before taking values
        if consts.CREATED in kwargs:
            self.created = Dated(**kwargs.get(consts.CREATED))
        if consts.UPDATED in kwargs:
            self.updated = Dated(**kwargs.get(consts.UPDATED))


class Dated:
    """
    Deserialization object for Dated object of Connect public API
    """

    def __init__(self, **kwargs):
        # Validate fields before taking values
        if consts.AT in kwargs:
            self.at = kwargs.get(consts.AT)
        if consts.BY in kwargs:
            self.by = Named(**kwargs.get(consts.BY))


class Marketplace(Named):
    """
    Deserialization object for Marketplace object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Validate fields before taking values
        if consts.ICON in kwargs:
            self.icon = kwargs.get(consts.ICON)


class Product(Named):
    """
    Deserialization object for Product object of Connect public API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Validate fields before taking values
        if consts.ICON in kwargs:
            self.icon = kwargs.get(consts.ICON)
        if consts.STATUS in kwargs:
            self.status = kwargs.get(consts.STATUS)


class Constraints:
    """
    Deserialization object for Constraints object of Connect public API
    """

    def __init__(self, **kwargs):
        # Validate fields before taking values
        if consts.REQUIRED in kwargs:
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

        # Validate fields before taking values
        if consts.TYPE in kwargs:
            self.type = kwargs.get(consts.TYPE)
        if consts.PROVIDER in kwargs:
            self.provider = Named(**kwargs.get(consts.PROVIDER))
        if consts.VENDOR in kwargs:
            self.vendor = Named(**kwargs.get(consts.VENDOR))
        if consts.HUB in kwargs:
            self.hub = Named(**kwargs.get(consts.HUB))
