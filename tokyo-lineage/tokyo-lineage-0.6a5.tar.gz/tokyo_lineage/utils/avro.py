import json
from typing import List

from avro import schema as avro_schema
from openlineage.common.dataset import Field


def get_avro_schema(schema: str):
    avro_schema_json = json.loads(schema)
    return avro_schema.parse(json.dumps(avro_schema_json))


def get_avro_fields(schema: str) -> List[Field]:
    _schema = get_avro_schema(schema)
    fields = _schema.props['fields']

    def filter_avro_field_type(types) -> str:
        if not hasattr(types, '_schemas'):
            try:
                return types.logical_type
            except:
                return types.type
        
        for f in types._schemas:
            if f.type != 'null':
                try:
                    return f.logical_type
                except:
                    return f.type

    fields = [
        Field(
            name=f.name,
            type=filter_avro_field_type(f.type)
        ) for f in fields
    ]

    return fields