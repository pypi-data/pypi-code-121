""" Creates entities from Dicts """


import json
from importlib import import_module
from pyclbr import Function
from typing import Dict, Sequence

from .attribute import Attribute
from .enum_attribute import EnumAttribute
from .blueprint_attribute import BlueprintAttribute
from .entity import Entity


class DMTReader():
    """ Creates entities from Dicts """

    class Reference:
        """Holds a reference until it can be resolved"""

        def __init__(self,entity, prop: Attribute,uid: str):
            self.entity = entity
            self.prop = prop
            self.uid = uid

    def __init__(self, external_refs: Dict[str,Entity]=dict()):
        self.entities = dict()
        self.unresolved = list()
        self.external_refs=external_refs

    def read(self, filename) -> Entity:
        """ Read entity from file """
        with open(filename, 'r',encoding="utf-8", errors='replace') as file:
            res=json.load(file)
            return self.from_dict(res)


    def from_dict(self,ent_dict: Dict) -> Entity:
        """ Create entity from Dict """
        entity=self.__from_dict(ent_dict)
        self.__resolve_all()
        return entity

    def from_dicts(self,ent_dicts: Sequence[Dict]) -> Sequence[Entity]:
        """ Create entity from Dict """
        entities = [self.__from_dict(e) for e in ent_dicts]
        self.__resolve_all()
        return entities

    def __resolve_all(self):
        for ref in self.unresolved:
            if not self.__resolve(ref):
                raise Exception(f"Unresolved reference: {ref}")


    def __from_dict(self,ent_dict: Dict) -> Entity:
        """ Read entities from Dict """
        entity_type: str=ent_dict["type"]
        constructor = self._resolve_type(entity_type)
        if not constructor:
            raise Exception(f"Unkown entity type {entity_type}")
        entity_instance: Entity = constructor()
        blueprint = entity_instance.blueprint
        for key, value in ent_dict.items():
            if key == "_id":
                uid = value
                self.entities[uid] = entity_instance
                continue
            if key == "type":
                continue
            attribute = blueprint.get_attribute(key)
            if not attribute:
                #FIXME
                continue
            if isinstance(attribute, BlueprintAttribute):
                self.__set_blueprint_value(entity_instance,attribute,value)
            elif attribute.is_enum:
                self.__set_enum_value(entity_instance,attribute,value)
            else:
                setattr(entity_instance,key, value)

        return entity_instance

    def _resolve_type(self, atype: str) -> Function:
        pkg: any = None
        parts = atype.split("/")
        if parts[0] == "":
            del parts[0]
        ename = parts.pop()
        package_path = ".".join(parts)
        try:
            pkg = import_module(package_path)
        except ModuleNotFoundError:
            raise Exception(f"Unable to load package {package_path}")
    
        constructor = pkg.__dict__.get(ename)
        return constructor

    def __set_blueprint_value(self,entity_instance: Entity, attribute: EnumAttribute,value):
        if attribute.contained:
            self.__set_value(entity_instance,attribute,value)
        else:
            self.__set_reference(entity_instance,attribute,value)

    def __set_reference(self,entity_instance: Entity,prop: Attribute,value):
        if isinstance(value, Dict):
            uid=value["_id"]
            ref = self.Reference(entity_instance,prop,uid)
            if not self.__resolve(ref):
                self.unresolved.append(ref)
        return

    def __set_value(self,entity_instance: Entity, attribute: BlueprintAttribute,value):
        if isinstance(value, Sequence):
            children = [self.__from_dict(v) for v in value]
            setattr(entity_instance,attribute.name, children)
        elif isinstance(value, Dict):
            child=self.__from_dict(value)
            if child:
                setattr(entity_instance,attribute.name, child)
        else:
            setattr(entity_instance,attribute.name, value)

    def __resolve(self, ref: Reference):
        value = self.entities.get(ref.uid,self.external_refs.get(ref.uid,None))
        if value:
            self.__set_value(ref.entity,ref.prop,value)
            return True

        return False

    def __set_enum_value(self,entity: Entity, attribute: EnumAttribute,value: str):
        """ Convert from string to Enum"""
        
        constructor = self._resolve_type(attribute.type)
        if not constructor:
            raise Exception(f"Unkown Enum type {attribute.type}")
        evalue = constructor[value]
        setattr(entity,attribute.name, evalue)
