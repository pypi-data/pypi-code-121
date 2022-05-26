
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.absence_api import AbsenceApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from redrover_api.api.absence_api import AbsenceApi
from redrover_api.api.absence_reason_api import AbsenceReasonApi
from redrover_api.api.absence_reason_balance_api import AbsenceReasonBalanceApi
from redrover_api.api.connection_api import ConnectionApi
from redrover_api.api.organization_api import OrganizationApi
from redrover_api.api.reference_data_api import ReferenceDataApi
from redrover_api.api.user_api import UserApi
from redrover_api.api.vacancy_api import VacancyApi
from redrover_api.api.webhooks_api import WebhooksApi
