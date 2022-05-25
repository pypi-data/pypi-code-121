from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Namespace(Base):
    """
    A Namespace objects structure.
    """

    properties = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "spec": Property(),        
        "metadata": Property(mutable=True),
        "created_at": Property(),  
        "status": Property(mutable=True)
    }  