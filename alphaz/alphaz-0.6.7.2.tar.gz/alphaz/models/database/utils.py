import importlib
import typing
from marshmallow import Schema
from marshmallow import fields as cfields
from marshmallow_sqlalchemy import ModelConverter, fields

from ...config.main_configuration import CONFIGURATION

from ..logger import AlphaLogger

SCHEMAS = {}
MODULES = {}
LOG = None

def __get_nested_schema(mapper, parent=None):
    auto_schema = get_auto_schema(mapper.entity)

    from core import core
    mapper_name = str(mapper).split('class ')[1].split('->')[0]
    schema_name = mapper_name + 'Schema'

    columns = []
    if hasattr(mapper,'columns'):
        for column in mapper.columns:
            columns.append(column.name)

    # Dynamic schema class creation
    properties = {
        'Meta':type('Meta', (object,),{'fields':columns})
    }
    schema = type(schema_name, (core.ma.Schema,),
        properties
    )
    return auto_schema

def get_auto_schema(model, relationship:bool=True,disabled_relationships:typing.List[str]=[]):    
    from core import core
    if CONFIGURATION.DEBUG_SCHEMA:
        core.log.debug(f"Getting auto schema for <{model.__name__}>")

    properties = {
        'Meta':type('Meta', (object,),
        {
            'model':model,
            'include_fk':True,
            "load_instance":True,
            "include_relationships":relationship
        })
    }
    schema = type(f"{model.__name__}Schema", (core.ma.SQLAlchemyAutoSchema,),
        properties
    )
    return schema

def generate_schema(class_obj, relationship:bool=True, disabled_relationships:typing.List[str]=None, parents:typing.List[str]=None):
    parents = parents or []
    disabled_relationships = disabled_relationships or []    

    schema_key = "-".join([f"{x}:{str(y)}" for x,y in locals().items()])
    if schema_key in SCHEMAS:
        return SCHEMAS[schema_key]

    schema_name = f"{class_obj.__name__}Schema"
    schema_full_name = schema_name if not relationship else f"{schema_name}_{'-'.join(disabled_relationships)}"
    if schema_full_name in parents:
        if CONFIGURATION.DEBUG_SCHEMA:
            from core import core
            core.log.error(f"Schema {schema_full_name} in parents {str(parents)}")
        relationship = False
        #return None

    auto_schema = get_auto_schema(class_obj,relationship=relationship)

    cols, related, related_list = {}, {}, {}
    for key, value in auto_schema._declared_fields.items():
        if type(value) == fields.Related and relationship:
            related[key] = value
        elif type(value) == fields.RelatedList and relationship:
            related_list[key] = value
        else:
            cols[key] = value

    columns, nesteds, list_nesteds = [], {}, {}
    for key, value in class_obj.__dict__.items():
        if key.startswith('__'): continue
        if not hasattr(value, "is_attribute") or not value.is_attribute: continue
        
        if hasattr(value, 'visible') and getattr(value, 'visible'):
            columns.append(key)
        elif hasattr(value,"entity") and relationship:
            if key in disabled_relationships:
                continue
            entity = value.entity.entity

            columns.append(key)
            #if parent is None or not schema_full_name in SCHEMAS:
            # nested_schema = __get_nested_schema(value.entity, parent=class_obj)
                #nested_schema = get_schema(value.entity.entity)
            #else:
            if CONFIGURATION.DEBUG_SCHEMA:
                from core import core
                core.log.error(f"Parent {schema_full_name} has a child named {key} with parents {str(parents)}")
            if not schema_full_name in parents:
                parents.append(schema_full_name)
            
            nested_schema = generate_schema(entity, relationship=relationship, disabled_relationships=disabled_relationships, parents=parents) #SCHEMAS[schema_full_name]
            
            if nested_schema is not None:
                if key in related:
                    nesteds[key] = nested_schema
                elif key in related_list:
                    list_nesteds[key] = nested_schema

    #g_s = ModelConverter()
    #flds = {x:y for x,y in g_s.fields_for_model(class_obj).items() if x in columns}

    for key, value in nesteds.items():
        cols[key] = fields.Nested(value)
    for key, value in list_nesteds.items():
        cols[key] = cfields.List(fields.Nested(value))
    generated_schema = Schema.from_dict(cols)

    SCHEMAS[schema_key] = generated_schema
    return generated_schema

def get_schema(class_obj, default:bool=False, relationship:bool=True, disabled_relationships:typing.List[str]=None):
    """ Get Schema for a model

    Args:
        class_obj ([type]): [description]
        parent ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    disabled_relationships =disabled_relationships or []

    schema_name = f"{class_obj.__name__}Schema"

    if default:
        module_name = class_obj.__module__
        if not module_name in MODULES:
            mod = importlib.import_module(module_name)  
            class_obj.log.info(f"Importing module <{module_name}>")
        else: 
            mod = MODULES[module_name]
        if hasattr(mod, schema_name):
            return getattr(mod, schema_name)
        else:
            class_obj.log.error(f"Cannot find a default schema in module <{module_name}>")
    generated_schema = generate_schema(class_obj, relationship=relationship, disabled_relationships=disabled_relationships)
    return generated_schema