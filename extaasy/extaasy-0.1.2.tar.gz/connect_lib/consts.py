#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
Module consts definition file
"""

# Connect Api Actions
TEMPLATE_ID = "template_id"
APPROVE = 'approve'
FAIL = 'fail'
MESSAGES = 'messages'
REASON = 'reason'

# Connect Request statuses
STATUS = 'status'
ACTIVE = 'active'
SUSPENDED = 'suspended'
PROCESSING = 'processing'

# Connect response "REQ_003 - Only pending and inquiring requests can be approved"
CONNECT_ERROR_CODE_APPROVE_NOT_PENDING_INQUIRING = 'REQ_003'

# REQUEST STRUCTURE
ID = 'id'
NAME = 'name'
TYPE = 'type'
ASSET = 'asset'
PARAMS = 'params'
VALUE = 'value'
VALUE_ERROR = 'value_error'
NOTE = 'note'
CREATED = 'created'
UPDATED = 'updated'
ANSWERED = 'answered'
ASSIGNEE = 'assignee'
ACTIVATION_KEY = 'activation_key'
PREVIOUS_APPROVED_REQUEST = 'previous_approved_request'
EFFECTIVE_DATE = 'effective_date'
PLANNED_DATE = 'planned_date'
EVENTS = 'events'
MARKETPLACE = 'marketplace'
CONTRACT = 'contract'
PHASE = 'phase'
DESCRIPTION = 'description'
TITLE = 'title'
CONSTRAINTS = 'constraints'
SCOPE = 'scope'
HINT = 'hint'
PLACEHOLDER = 'placeholder'
GLOBAL_ID = 'global_id'
MPN = 'mpn'
OLD_QUANTITY = 'old_quantity'
QUANTITY = 'quantity'
DISPLAY_NAME = 'display_name'
PERIOD = 'period'
ITEM_TYPE = 'item_type'
EXTERNAL_ID = 'external_id'
EXTERNAL_UID = 'external_uid'
PRODUCT = 'product'
CONNECTION = 'connection'
ITEMS = 'items'
TIERS = 'tiers'
CUSTOMER = 'customer'
TIER1 = 'tier1'
TIER2 = 'tier2'
CONFIGURATION = 'configuration'
VERSION = 'version'
PARENT = 'parent'
OWNER = 'owner'
SCOPES = 'scopes'
HUB = 'hub'
TAX_ID = 'tax_id'
CONTACT_INFO = 'contact_info'
ADDRESS_LINE1 = 'address_line1'
ADDRESS_LINE2 = 'address_line2'
CITY = 'city'
STATE = 'state'
POSTAL_CODE = 'postal_code'
COUNTRY = 'country'
CONTACT = 'contact'
FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
EMAIL = 'email'
PHONE_NUMBER = 'phone_number'
COUNTRY_CODE = 'country_code'
AREA_CODE = 'area_code'
EXTENSION = 'extension'
AT = 'at'
BY = 'by'
ICON = 'icon'
REQUIRED = 'required'
META = 'meta'
MAX_LENGTH = 'max_length'
MIN_LENGTH = 'min_length'
HIDDEN = 'hidden'
UNIQUE = 'unique'
RECONCILIATION = 'reconciliation'
SHARED = 'shared'
PROVIDER = 'provider'
VENDOR = 'vendor'

# logger fields
PARAMETER = 'parameter'
PASSWORD = 'password'
AUTHORIZATION = 'Authorization'
TOKEN = 'token'
TASK_ID = 'task_id'

# Connect: conversation payload message
TEXT = 'text'
