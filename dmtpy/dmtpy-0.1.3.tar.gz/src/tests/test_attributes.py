import json
from dmt.attribute import Attribute
from dmt.blueprint import Blueprint
from dmt.dmt_writer import DMTWriter
from tests.test_entity import TestEntity


def test_attribute_creation():

    attribute = Attribute("myint", "integer", "description")
    assert attribute.name is "myint"
    assert attribute.is_primitive


def test_write_attribute_when_default():

    attribute = Attribute("myint", "integer", "description", optional=False, default=1)
    assert attribute.name is "myint"
    assert attribute.is_primitive
    blueprint = Blueprint(name="BP", package_path="")
    blueprint.attributes.append(attribute)
    entity = TestEntity(blueprint)
    entity.myint = 2
    writer = DMTWriter()
    res = writer.to_dict(entity)
    assert res.get("myint") is 2
    entity.myint = 1
    res = writer.to_dict(entity)
    assert (
        res.get("myint") is 1
    ), "The default value was used, but the attribute is not optional and should have been written"
    attribute.optional = True
    res = writer.to_dict(entity)
    assert "myint" not in res
