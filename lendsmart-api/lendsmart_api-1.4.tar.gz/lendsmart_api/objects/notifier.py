from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Notifier(Base):
    """
    A Notifier objects structure.
    """

    properties = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "email": Property(),   
        "confirm_token": Property(), 
        "confirm_password": Property(),    
        "confirm_type": Property(),      
        "metadata": Property(mutable=True),
        "created_at": Property(),  
    }  

