from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class LendingTerm(Base):
    """
    A Document is something a LendSmart customer uploads.
    """
    api_endpoint = '/lending_terms'

    properties = {
        "id": Property(identifier=True),
        "label": Property(mutable=True),
        "description": Property(mutable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "metadata": Property(mutable=True),
        "status": Property(),
        "created": Property(is_datetime=True),
        "created_at": Property(),
        "case_detail": Property(),
        "terms": Property(),
        "size": Property(),
        "deprecated": Property(),
        "updated_at": Property()
    }
