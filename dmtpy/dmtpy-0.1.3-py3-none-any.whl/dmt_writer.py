""" Export entites as SIMA objects"""


from enum import Enum
import json
from typing import Dict, Sequence
import uuid
from .attribute import Attribute
from .blueprint_attribute import BlueprintAttribute
from .entity import Entity


class DMTWriter:
    """Convert to DMT dictionary"""

    def __init__(self, use_external_refs=False):
        self.uuids = dict()
        self.use_external_refs=use_external_refs
        self.external_refs: Dict[str,Entity] = dict()
    
    def write(self, entity: Entity, filename, indent=0):
        """Write entity to file"""
        with open(filename, "w", encoding="utf-8") as file:
            res = self.to_dict(entity)
            json.dump(res, file, indent=indent)

    def to_dicts(self, entities: Sequence[Entity]) -> Sequence[Dict]:
        """Convert to DMT dictionaries"""

        # Make sure all referenced enitites has id's
        for entity in entities:
            self.__set_alls_ids(entity)

        return [self.__as_dict(entity) for entity in entities]

    def to_dict(self, entity: Entity) -> Dict:
        """Convert to DMT dictionary"""
        return self.to_dicts([entity])[0]

    def __as_dict(self, entity: Entity):
        """Convert to dictionary"""
        blueprint = entity.blueprint
        ret = {"type": blueprint.get_path()}
        for attribute in blueprint.attributes:
            if entity.is_set(attribute):
                value = self.__attribute_dict(entity, attribute)
                if value is not None:
                    ret[attribute.name] = value
        _id = self.uuids.get(entity, None)
        if _id:
            ret["_id"] = _id
        return ret

    def __attribute_dict(self, entity: Entity, attribute: Attribute):
        value = getattr(entity, attribute.name, None)
        if isinstance(attribute, BlueprintAttribute):
            if not attribute.contained:
                # This is a cross reference
                reference: Entity = value
                _id = self.uuids.get(reference, None)
                if not _id:
                    if self.use_external_refs:
                        _id = self.external_refs.get(reference, None)
                        if not _id:
                            _id = str(uuid.uuid4())
                            self.external_refs[_id]=reference
                        return {"_id": _id}
                    else:
                        raise Exception("Id not set")
                return {"_id": _id}
            if attribute.has_dimensions():
                values = [self.__as_dict(lvalue) for lvalue in value]
                return values
            else:
                return self.__as_dict(value)
        else:
            if attribute.is_primitive:
                if attribute.has_dimensions():
                    try:
                        # Assumes ndarray..
                        return value.tolist()
                    except AttributeError:
                        return value
                else:
                    if self.__is_optional_default(attribute, value):
                        return None
                    return value
            else:
                if attribute.is_enum:
                    enum: Enum = value
                    return enum.name
                return self.__as_dict(value)

    def __set_alls_ids(self, entity: Entity):
        for child in entity.all_content():
            for atribute in child.blueprint.blueprint_attributes():
                if not atribute.contained and child.is_set(atribute):
                    self.__set_id(child, atribute)

    def __set_id(self, entity: Entity, attribute: BlueprintAttribute):
        uuids = self.uuids
        value = getattr(entity, attribute.name, None)
        if attribute.has_dimensions():
            entities: Sequence[Entity] = value
            for entity in entities:
                if entity not in uuids:
                    uuids[entity] = str(uuid.uuid4())
        else:
            entity: Entity = value
            if entity not in uuids:
                uuids[entity] = str(uuid.uuid4())

    def __is_optional_default(self, attribute: Attribute, value: any):
        if attribute.optional and attribute.is_primitive:
            return value == attribute.default
        return False
