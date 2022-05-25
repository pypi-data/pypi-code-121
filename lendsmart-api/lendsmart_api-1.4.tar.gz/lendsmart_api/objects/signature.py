from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class AccountSign(Base):
    """
    An AccountSign is something a LendSmart customer uploads.
    """
    api_endpoint = '/account_signs'

    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "coborrower": Property(),
        "borrower": Property(),
    }
