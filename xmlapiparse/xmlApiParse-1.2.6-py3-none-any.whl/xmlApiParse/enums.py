from enum import Enum


class SpecificCollectionsEnum(Enum):
    order_types = 'UNCHANGEABLEORDERTYPES'
    scheme_details = 'modischemedetails'
    currencies = 'CURRENCIES'
    menu_items = 'MENUITEMS'
    employees = 'Employees'
    modidiers = 'MODIFIERS'
    tables = 'Tables'
    cashes = 'Cashes'
    classificator = 'CLASSIFICATORGROUPS'
    category = 'CATEGLIST'


class AllCollectionsEnum(Enum):
    system_info = 'GetSystemInfo'
    order_list = 'GetOrderList'
    reference = 'GetRefList'
