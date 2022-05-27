import os, base64
from ddd_objects.domain.value_obj import ExpiredValueObject
from ddd_objects.domain.exception import ParameterError, FormatError

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

class SecurityGroupID(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class InstanceType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Hostname(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

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
    def is_available(self):
        return self.value=='Available'
class InstanceTypeStatusCategory(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)
    def is_with_stock(self):
        return self.value=='WithStock'
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
    def add(self, s):
        self.value += s
        return self

class Type(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)

class Path(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)
    def get_base_name(self)->str:
        return os.path.basename(self.value)

class NodeType(Type):
    def __init__(self, value):
        super().__init__(value)
    def is_master(self):
        return self.value=='master'

class NodeName(Name):
    def __init__(self, value):
        super().__init__(value)
    def get_cluster_name(self):
        cluster_name = self.value.split('-')[0]
        if cluster_name[-1] == '*':
            cluster_name = cluster_name[:-1]
        return Name(cluster_name)
    def get_master_name(self):
        master_name = self.value.split('-')[0]+'-master'
        return Name(master_name)
    def get_node_type(self):
        parts = self.value.split('-')[1:-1]
        return NodeType('-'.join(parts))
    def get_type_group_name(self):
        parts = self.value.split('-')[:-1]
        type_group_name = '-'.join(parts)
        return Name(type_group_name)
    def check_name(self, node_type:NodeType):
        parts = self.value.split('-')
        main_part = '-'.join(parts[1:])
        if not main_part.startswith(node_type.get_value()):
            raise FormatError('Wrong format of node name')

class NodeStatus(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)
    def is_ready(self):
        return 'NotReady' not in self.value
    def is_schedulable(self):
        return 'SchedulingDisabled' not in self.value

class YamlString(ExpiredValueObject):
    def __init__(self, value):
        if isinstance(value, int) or isinstance(value, float) \
            or (isinstance(value, str) and value.isdigit()):
            value = f'"{value}"'
        elif not isinstance(value, str):
            raise ValueError(f'Type {type(value)} is not supported')
        super().__init__(value)

class Base64String(ExpiredValueObject):
    def __init__(self, value):
        value = str(base64.b64encode(value.encode('utf-8')),"utf-8")
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

class Subdomain(ExpiredValueObject):
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

class ServiceType(ExpiredValueObject):
    def __init__(self, value):
        super().__init__(value, None)