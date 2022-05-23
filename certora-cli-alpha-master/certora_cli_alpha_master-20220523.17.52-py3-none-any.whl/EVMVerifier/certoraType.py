from typing import Any, Dict, List, Optional, Callable

from EVMVerifier.certoraNodeFilters import NodeFilters
import logging

ast_logger = logging.getLogger("ast")


class Type:
    def __init__(self, name: str, type_string: str):
        self.name = name
        self.type_string = type_string

    # I'm not messing with __eq__ right now
    def matches(self, other: Any) -> bool:
        if not isinstance(other, Type):
            # don't attempt to compare against unrelated types
            return NotImplemented
        if isinstance(other, UserDefinedType) and isinstance(self, UserDefinedType):
            return self.canonical_name == other.canonical_name
        elif isinstance(other, MappingType) and isinstance(self, MappingType):
            return self.type_string == other.type_string
        elif isinstance(other, ArrayType) and isinstance(self, ArrayType):
            return self.type_string == other.type_string
        else:
            # hope I got all cases, luv2python
            return self.type_string == other.type_string

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name,
                "type": "Primitive",
                "canonicalName": None,
                "contractName": None,
                "members": None}

    @staticmethod
    def from_primitive_name(name: str) -> 'Type':
        return Type(name, name)

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]], def_node: Dict[str, Any]) -> 'Type':
        if NodeFilters.is_enum_definition(def_node):
            ret = EnumType.from_def_node(lookup_reference, def_node)  # type: Type
        elif NodeFilters.is_struct_definition(def_node):
            ret = StructType.from_def_node(lookup_reference, def_node)
        elif NodeFilters.is_user_defined_value_type_definition(def_node):
            ret = UserDefinedValueType.from_def_node(lookup_reference, def_node)
        elif NodeFilters.is_contract_definition(def_node):
            ret = Type("address", "address")  # TODO: payable and shit?
        else:
            ast_logger.fatal(f"unexpected AST Type Definition Node {def_node}")
        return ret

    @staticmethod
    def from_type_name_node(lookup_reference: Callable[[int], Dict[str, Any]], type_name: Dict[str, Any]) -> 'Type':
        if type_name["nodeType"] == "ElementaryTypeName":
            ret = Type(type_name["name"], type_name["typeDescriptions"]["typeString"])  # type: Type
        elif type_name["nodeType"] == "FunctionTypeName":
            # TODO what to do with FunctionTypes :[]
            name = type_name["typeDescriptions"]["typeString"]
            ret = Type(name, name)
        elif type_name["nodeType"] == "UserDefinedTypeName":
            ret = UserDefinedType.from_def_node(lookup_reference, lookup_reference(
                type_name["referencedDeclaration"]))
        elif type_name["nodeType"] == "Mapping":
            ret = MappingType.from_def_node(lookup_reference, type_name)
        elif type_name["nodeType"] == "ArrayTypeName":
            ret = ArrayType.from_def_node(lookup_reference, type_name)
        else:
            ast_logger.fatal(f"unexpected AST Type Name Node: {type_name}")
        return ret


class MappingType(Type):
    def __init__(self, type_string: str, domain: Type, codomain: Type, contract_name: str, reference: int):
        Type.__init__(self, f"mapping({domain.name} => {codomain.name})", type_string)
        self.domain = domain
        self.codomain = codomain
        self.contract_name = contract_name
        self.reference = reference

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]], def_node: Dict[str, Any]) -> 'MappingType':
        domain = Type.from_type_name_node(lookup_reference, def_node["keyType"])
        codomain = Type.from_type_name_node(lookup_reference, def_node["valueType"])
        type_string = def_node["typeDescriptions"]["typeString"]
        return MappingType(
            type_string=type_string,
            domain=domain,
            codomain=codomain,
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"]
        )

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name,
                "type": "Mapping",
                "canonicalName": None,
                "contractName": self.contract_name,
                "members": None,
                "domain": self.domain.as_dict(),
                "codomain": self.codomain.as_dict()}


class ArrayType(Type):
    def __init__(self, type_string: str, elementType: Type, length: Optional[int], contract_name: str, reference: int):
        Type.__init__(self, type_string, type_string)
        self.elementType = elementType
        self.length = length  # a length of None indicates a dynamic array
        self.contract_name = contract_name
        self.reference = reference

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]], def_node: Dict[str, Any]) -> 'ArrayType':
        type_string = def_node["typeDescriptions"]["typeString"]
        element_type = Type.from_type_name_node(lookup_reference, def_node["baseType"])
        if "length" in def_node.keys() and def_node["length"] is not None:
            length = int(def_node["length"]["value"], 10)  # type: Optional[int]
        else:
            length = None
        return ArrayType(
            type_string=type_string,
            elementType=element_type,
            length=length,
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"]
        )

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name,
                "type": "Array",
                "canonicalName": None,
                "contractName": self.contract_name,
                "members": None,
                "elementType": self.elementType.as_dict(),
                "length": self.length}


class UserDefinedType(Type):
    def __init__(self, name: str, type_string: str, canonical_name: str, contract_name: str, reference: int):
        Type.__init__(self, name, type_string)
        self.canonical_name = canonical_name
        self.contract_name = contract_name
        self.reference = reference

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "canonicalName": self.canonical_name,
            "contractName": self.contract_name,
            "type": None
        }

    @staticmethod
    def get_type_string_from_def_node(def_node: Dict[str, Any]) -> str:
        if "typeDescriptions" in def_node.keys():
            return def_node["typeDescriptions"]["typeString"]  # was'nt included in solidity 4ish
        else:
            canonical_name = def_node["canonicalName"]
            return f"enum {canonical_name}"


class EnumType(UserDefinedType):
    def __init__(self, name: str, type_string: str, canonical_name: str, members: List[str], contract_name: str,
                 reference: int):
        UserDefinedType.__init__(self, name, type_string, canonical_name, contract_name, reference)
        self.members = members

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]], def_node: Dict[str, Any]) -> 'EnumType':
        members = map(
            lambda member: member["name"],
            def_node["members"]
        )

        return EnumType(
            name=def_node["name"],
            type_string=UserDefinedType.get_type_string_from_def_node(def_node),
            canonical_name=def_node["canonicalName"],
            members=list(members),
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"]
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "Enum",
            "name": self.name,
            "canonicalName": self.canonical_name,
            "members": [{"name": x, "type": None} for x in self.members],
            "contractName": self.contract_name  # null means it wasn't declared in a contract but at file-level
        }


class StructType(UserDefinedType):
    def __init__(self, name: str, type_string: str, canonical_name: str, members: List[Any], contract_name: str,
                 reference: int):
        UserDefinedType.__init__(self, name, type_string, canonical_name, contract_name, reference)
        self.members = members

    class StructMember:
        def __init__(self, name: str, type: Type):
            self.name = name
            self.type = type

        @staticmethod
        def from_member_node(lookup_reference: Callable[[int], Dict[str, Any]],
                             member_node: Dict[str, Any]) -> 'StructType.StructMember':
            name = member_node["name"]
            type_name = member_node["typeName"]
            type = Type.from_type_name_node(lookup_reference, type_name)
            assert type is not None
            return StructType.StructMember(name, type)

        def as_dict(self) -> Dict[str, Any]:
            return {
                "name": self.name,
                "type": self.type.as_dict()
            }

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]], def_node: Dict[str, Any]) -> 'StructType':
        canonical_name = def_node["canonicalName"]
        return StructType(
            name=def_node["name"],
            type_string=f"struct {canonical_name}",
            canonical_name=canonical_name,
            members=[StructType.StructMember.from_member_node(lookup_reference, member_node) for member_node in
                     def_node["members"]],
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"]
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "Struct",
            "name": self.name,
            "canonicalName": self.canonical_name,
            "members": [x.as_dict() for x in self.members],
            "contractName": self.contract_name
            # ^ null means it wasn't declared in a contract but at file-level (is this possible for structs?)
        }


# Solidity Name for a Type Alias
class UserDefinedValueType(UserDefinedType):
    def __init__(self, name: str, canonical_name: str, contract_name: str, reference: int, underlying: Type):
        UserDefinedType.__init__(self, name, canonical_name, canonical_name, contract_name, reference)
        self.underlying = underlying

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]],
                      def_node: Dict[str, Any]) -> 'UserDefinedValueType':
        return UserDefinedValueType(
            name=def_node["name"],
            canonical_name=def_node["canonicalName"],
            contract_name=def_node.get(NodeFilters.CERTORA_CONTRACT_NAME(), None),
            reference=def_node["id"],
            underlying=Type.from_type_name_node(lookup_reference, def_node["underlyingType"])
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "UserDefinedValueType",
            "name": self.name,
            "canonicalName": self.canonical_name,
            "members": None,
            "contractName": self.contract_name,
            "underlying": self.underlying.as_dict()
        }


class ContractType(UserDefinedType):
    def __init__(self, name: str, reference: int):
        # TODO: should we allow contract_name for inner/nested contract declarations?
        UserDefinedType.__init__(self, name, name, name, name,  # is name right for typeString?
                                 reference)

    @staticmethod
    def from_def_node(lookup_reference: Callable[[int], Dict[str, Any]], def_node: Dict[str, Any]) -> 'ContractType':
        name = def_node["name"]
        id = def_node["id"]
        return ContractType(name, id)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "type": "Contract",
            "name": self.name,
            "canonicalName": self.canonical_name,
            "members": None,
            "contractName": self.contract_name
        }
