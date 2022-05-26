from projectal.entity import Entity
from projectal.linkers import *


class Customer(Entity, ContactLinker, FileLinker, LocationLinker):
    """
    Implementation of the [Customer](https://projectal.com/docs/latest/#tag/Customer) API.
    """
    _path = 'customer'
    _name = 'CUSTOMER'
