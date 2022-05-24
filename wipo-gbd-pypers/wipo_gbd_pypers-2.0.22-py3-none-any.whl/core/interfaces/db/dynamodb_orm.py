from dynamorm import DynaModel

from marshmallow import fields
import os
from pypers.core.interfaces.config import pypers_schema_db
from pypers.core.interfaces.db.base import DbBase

if os.environ.get('DYDB_URL', None):
    endpoint_url = os.environ['DYDB_URL']
else:
    endpoint_url = None


class GenericTableMetaclass(type):

    @classmethod
    def _convert_class_name_to_table_name(cls, name):
        name = name.replace('.Table', '')
        new_name = ''
        tmp = name.lower()
        for idx in range(0, len(name)):
            if name[idx] != tmp[idx]:
                new_name += '_'
            new_name += tmp[idx]
        return new_name[1:]

    @classmethod
    def _get_config_from_name(cls, name):
        for key in dir(pypers_schema_db):
            if getattr(pypers_schema_db, key)['name'] == name:
                return getattr(pypers_schema_db, key)

    def __new__(cls, name, bases, attrs):
        attrs['name'] = cls._convert_class_name_to_table_name(attrs['__qualname__'])
        config = cls._get_config_from_name(attrs['name'])
        for index in config['indexes'][0]:
            if index['primary_index']:
                attrs['hash_key'] = index['name']
            else:
                attrs['range_key'] = index['name']
        DbBase(endpoint='DYDB_URL', config=config)
        attrs['read'] = config.get('read', 5)
        attrs['write'] = config.get('write', 5)
        attrs['resource_kwargs'] = {
            'endpoint_url': endpoint_url
        }
        return super().__new__(cls, name, bases, attrs)


class GbdPypersRunConfig(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        runid = fields.String()
        collection = fields.String()
        pipeline_configuration = fields.Dict()
        gbd_ttl = fields.Int()
        version = fields.Int()


class GbdPypersRunConfigSteps(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        runid_collection = fields.String()
        step_name = fields.String()
        payload = fields.Dict()
        gbd_ttl = fields.Int()
        version = fields.Int()

class GbdPypersConfig(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        name = fields.String()
        pipeline_type = fields.String()
        json = fields.Dict()


class GbdConfig(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        uid = fields.String()
        conf = fields.Dict()


class GbdPypersErrors(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        time = fields.String()
        runid = fields.String()
        collection = fields.String()
        original_message = fields.Dict()
        error_trace = fields.String()


class GbdPypersDoneArchive(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        gbd_collection = fields.String()
        archive_name = fields.String()
        run_id = fields.String()
        process_date = fields.String()


class GbdPypersLogs(DynaModel):
    class Table(metaclass=GenericTableMetaclass): pass
    class Schema:
        runid_collection = fields.String()
        log_time = fields.String()
        l_type = fields.String()
        payload = fields.Dict()
        step = fields.String(allow_none=True)
