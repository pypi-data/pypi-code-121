#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bson import ObjectId
import time, datetime
import mongoengine
from sqlalchemy.ext.declarative import declarative_base

ModelBase = declarative_base()

def model_columns(model):
    if isinstance(model, mongoengine.Document) or hasattr(model, '_reverse_db_field_map'):
        columns = [k for k in model._fields]
        pk = model._reverse_db_field_map.get('_id')
        return columns, pk
    columns = []
    pk = None
    cls_ = model._sa_class_manager.class_
    ref = model._sa_class_manager.deferred_scalar_loader.args[0]
    colmaps = {}
    for k in model._sa_class_manager._all_key_set:
        c = getattr(cls_, k)
        colmaps[c.expression.key] = c.key
    tbl = None
    if ref.primary_key:
        pk = colmaps[ref.primary_key[0].name]
    for t in ref.tables:
        if t.name == ref.local_table.name:
            tbl = t
            break
    if tbl is not None:
        for k in tbl.columns._all_columns:
            columns.append(colmaps[str(k.key)])
    else:
        for k in model._sa_class_manager._all_key_set:
            columns.append(str(k))
    return columns, pk

class MongoBase(mongoengine.DynamicDocument, metaclass=mongoengine.base.TopLevelDocumentMetaclass):
    """
    mongo模型基类
    """
    my_metaclass = mongoengine.base.TopLevelDocumentMetaclass

    def __init__(self, *args, **values):
        super(MongoBase, self).__init__(*args, **values)
        if not hasattr(self, 'obsoleted'):
            setattr(self, 'obsoleted', False)
        if not hasattr(self, 'created_at'):
            setattr(self, 'created_at', int(time.time()*1000))
        if not hasattr(self, 'updated_at'):
            setattr(self, 'updated_at', int(time.time()*1000))
        if not hasattr(self, 'sort_value'):
            setattr(self, 'sort_value', 1)
        # if not hasattr(self, 'created_by'):
        #     setattr(self, 'created_by',  None)
        # if not hasattr(self, 'updated_by'):
        #     setattr(self, 'updated_by',  None)

    def set_created(self, userId):
        self.created_by = userId

    def set_updated(self, userId):
        self.updated_by = userId

    def as_dict(self):
        result = {}
        for k in self:
            v = self[k]
            if isinstance(v, object):
                v = str(v)
            elif isinstance(v, datetime.datetime):
                v = str(v)
            result[k] = v
        return result

def format_mongo_value(v):
    if isinstance(v, ObjectId):
        return str(v)
    elif isinstance(v, mongoengine.Document):
        return {f: format_mongo_value(getattr(v, f)) for f in v}
    elif isinstance(v, datetime.datetime):
        return str(v)
    return v

MODEL_DB_MAPPING = {}
DEFAULT_SKIP_FIELDS = {'obsoleted':True, 'created_at':True, 'updated_at':True, 'created_by':True, 'updated_by':True}

def get_dbinstance_by_model(model_name):
    if model_name in MODEL_DB_MAPPING:
        return MODEL_DB_MAPPING[model_name]
    return ''

def set_model_dbinstance(model_instance_mapping: dict):
    if isinstance(model_instance_mapping, dict):
        for k, v in model_instance_mapping.items():
            MODEL_DB_MAPPING[k] = str(v)

def get_model_class_name(model) -> str:
    if hasattr(model, '_sa_class_manager'):
        return str(model._sa_class_manager.class_.__name__)
    elif hasattr(model, '__name__'):
        return model.__name__
    elif isinstance(model, str):
        return model
    return model.__class__.__name__
