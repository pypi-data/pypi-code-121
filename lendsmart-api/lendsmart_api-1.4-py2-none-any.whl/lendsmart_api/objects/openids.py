from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Openids(Base):
    """
    A openids objects structure.
    """

    properties = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "can_open": Property(),        
        "metadata": Property(mutable=True)
    } 