from ddd_objects.domain.value_obj import ExpiredValueObject
from ddd_objects.domain.exception import ParameterError

class Number(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Size(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class ID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Status(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class SecurityGroupID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InstanceType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Hostname(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class IngressHost(ExpiredValueObject):
    def __init__(self, value):
        self.parts = value.split('.')
        if len(self.parts)>3 or len(self.parts)==1:
            raise ParameterError('Invaild value')
        super().__init__(value, None)
    def get_domain_name(self):
        if len(self.parts)==2:
            return DomainName(self.value)
        elif len(self.parts)==3:
            return DomainName('.'.join(self.parts[-2:]))
    def get_subdomain(self):
        if len(self.parts)==2:
            return Subdomain('@')
        elif len(self.parts)==3:
            return Subdomain(self.parts[0])

class Price(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class ImageID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class RegionID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class ZoneID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InternetPayType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class PayType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class DateTime(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class IP(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class BandWidth(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Password(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Data(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Bool(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Command(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Username(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Port(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Output(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InstanceID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InstanceName(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Endpoint(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Token(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class NodeLabel(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Usage(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class GPUType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InstanceTypeStatus(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InstanceTypeStatusCategory(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Time(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Version(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Name(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)
    def match(self, value):
        return self.value==value

class Type(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Path(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class NodeName(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class NodeType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class NodeStatus(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class TimeInterval(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Key(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Value(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class KeyType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Info(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class DomainName(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class RecordID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Weight(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class DNSType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class DNSLine(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class SubdomainName(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Subdomain(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)