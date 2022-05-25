from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Document(Base):
    """
    A Document is something a LendSmart customer uploads.
    """
    api_endpoint = '/documents'

    properties = {
        "id": Property(identifier=True),
        "label": Property(mutable=True),
        "description": Property(mutable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "status": Property(),
        "created": Property(is_datetime=True),
        "created_by": Property(),
        "type": Property(),
        "is_public": Property(),
        "vendor": Property(),
        "size": Property(),
        "deprecated": Property(),
        "updated_at": Property()
    }
