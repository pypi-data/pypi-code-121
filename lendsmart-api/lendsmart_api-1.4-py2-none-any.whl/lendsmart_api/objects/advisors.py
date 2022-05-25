from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Advisors(Base):
    """
    A Advisors objects structure.
    """

    properties = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "email": Property(),  
        "source_id": Property(),     
        "first_name": Property(),  
        "last_name": Property(),  
        "social_security_no": Property(),  
        "birth_day": Property(),  
        "address": Property(),  
        "gender": Property(),  
        "phone": Property(),  
        "user_name ": Property(),    
        "metadata": Property(mutable=True),
        "business_name": Property(),  
        "license": Property(mutable=True),  
        "persona": Property(),  
        "description": Property(),  
        "avatar": Property(),  
        "created_at": Property(is_datetime=True),  
        "status": Property(mutable=True)
    } 