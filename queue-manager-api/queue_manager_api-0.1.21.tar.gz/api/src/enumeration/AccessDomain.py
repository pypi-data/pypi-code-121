from python_framework import Enum, EnumItem


@Enum()
class AccessDomainEnumeration :
    API = EnumItem()
    USER = EnumItem()
    ADMIN = EnumItem()


AccessDomain = AccessDomainEnumeration()
