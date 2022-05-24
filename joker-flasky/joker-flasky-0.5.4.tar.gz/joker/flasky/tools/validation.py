#!/usr/bin/env python3
# coding: utf-8

import jsonschema

from volkanic import errors


def make_object_schema(properties: dict, **kwargs):
    return {"type": "object", "properties": properties, **kwargs}


def human_lang_join(phrases: list, conj='and', punct=',', sep=' '):
    if not phrases:
        return ''
    if len(phrases) == 1:
        return phrases[0]
    parts = [s + punct for s in phrases[:-2]]
    parts.extend([phrases[-2], conj, phrases[-1]])
    return sep.join(parts)


def validate(data, schema, *args, **kwargs):
    try:
        jsonschema.validate(data, schema, *args, **kwargs)
    except jsonschema.ValidationError as ve:
        if msg := ve.schema.get('errmsg'):
            raise errors.BusinessError(msg)
        raise errors.TechnicalError(ve.absolute_path[-1], 'ValidationError')


class SchemaOutliner:
    _schema_types = [
        (bool, 'boolean'),
        (int, 'integer'),
        (float, 'number'),
        (list, 'array'),
        (dict, 'object'),
        (str, 'string'),
    ]

    def __init__(self, nullable=False, flattype=False):
        self.nullable = nullable
        self.flattype = flattype

    def expand_type(self, jstype: str):
        if self.nullable:
            return [jstype, 'null']
        elif self.flattype:
            return jstype
        return [jstype]

    def _infer_type(self, val):
        for pytype, jstype in self._schema_types:
            if isinstance(val, pytype):
                return jstype

    def infer_property(self, key: str, val):
        jstype = self._infer_type(val)
        if not jstype:
            return {}
        jstype = self.expand_type(jstype)
        typmsg = human_lang_join(jstype, 'or')
        return {
            'type': jstype,
            'errmsg': f'<{key}> must be of type {typmsg}',
        }

    def __call__(self, data: dict):
        assert isinstance(data, dict)
        properties = {}
        for key, val in data.items():
            properties[key] = self.infer_property(key, val)
        return make_object_schema(properties)
