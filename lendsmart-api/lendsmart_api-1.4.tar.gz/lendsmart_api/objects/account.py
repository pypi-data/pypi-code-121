from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Account(Base):
    """
    A Notifier objects structure.
    """

    properties = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "email": Property(),   
        "password": Property(), 
        "first_name": Property(),    
        "last_name": Property(),      
        "home_phone": Property(),
        "status": Property(),
        "avatar": Property(),
        "metadata": Property(),
        "is_admin": Property(),
        "cellmobile_phone": Property(),
        "created_at": Property(),  
    }  

