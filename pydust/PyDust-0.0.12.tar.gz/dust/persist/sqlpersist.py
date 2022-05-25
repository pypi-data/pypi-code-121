from enum import Enum
from jinja2 import Template
import traceback
import json

from dust import Datatypes, ValueTypes, Operation, MetaProps, FieldProps, Committed
from dust.entity import UNIT_ENTITY, EntityTypes, EntityBaseMeta, Store, UnitMeta
from dust.events import UNIT_EVENTS, EventTypes

_sql_persister = None
_types_initiated = set()

def init_sql_persist(unit_name, persist_class, meta_type_enums, deps_func):
    global _sql_persister
    global _types_initiated

    if not meta_type_enums in _types_initiated:
        print("Persist: Initiating {}/{}".format(unit_name, meta_type_enums.__name__))
        _types_initiated.add(meta_type_enums)

        if _sql_persister is None:
            _sql_persister = persist_class()
            print(str(_sql_persister))

        _sql_persister.generate_schema(unit_name, meta_type_enums)

        if deps_func:
            unit_dependencies = deps_func()
            if unit_dependencies:
                for dep_unit_name, dep_meta_type_enums, dep_deps_func in unit_dependencies:
                    init_sql_persist(dep_unit_name, persist_class, dep_meta_type_enums, dep_deps_func)

def load_all():
    global _sql_persister
    return _sql_persister.load_all()    

def load_units():
    global _sql_persister
    return _sql_persister.load_units()    

def load_unit_type(unit_meta_type):
    global _sql_persister
    return _sql_persister.load_type(unit_meta_type)    

def persist_entities(entities):
    global _sql_persister
    _sql_persister.persist_entities(entities)    

class SqlField():
    def __init__(self, field_name, field_type, primary_key=False, base_field=False):
        self.field_name = field_name
        self.field_type = field_type
        self.primary_key = primary_key
        self.base_field = base_field

class SqlTable():
    def __init__(self, table_name):
        self.table_name = table_name
        self.fields = []
        self.primary_keys = []

    def add_field(self, sql_field, sql_type, primary_key=False, base_field=False):
        field = SqlField(sql_field, sql_type, primary_key, base_field)
        self.fields.append(field)
        if primary_key:
            self.primary_keys.append(field)

class SqlPersist():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.__persisted_types = set()
        self.__unit_meta_unit = {}

    def table_exits(self, table_name, conn):
        pass 

    def sql_type(self, datatype, valuetype, primary_key=False):
        pass

    def create_table_template(self, sql_table):
        pass 

    def create_table(self, sql, conn):
        pass

    def insert_into_table_template(self):
        pass

    def select_template(self, filters):
        pass

    def update_template(self):
        pass

    def delete_template(self):
        pass

    def convert_value_to_db(self, field, value):
        pass

    def create_cursor(self, conn):
        pass

    def close_cursor(self, conn):
        pass

    def create_exectute_params(self):
        pass

    def add_execute_param(self, values, name, value):
        pass

    def map_value_to_db(self, field, entity):
        value = entity.access(Operation.GET, None, field)
        if value is None:
            return None 
        else:
            if field.valuetype == ValueTypes.SINGLE:
                return self.convert_value_to_db(field, value)

            elif field.valuetype == ValueTypes.SET:
                return [self.convert_value_to_db(field, v) for v in value]

            elif field.valuetype == ValueTypes.LIST:
                return [self.convert_value_to_db(field, v) for v in value]

            elif field.valuetype == ValueTypes.MAP:
                return json.dumps(value)

    def map_value_from_db(self, field, value):
        if value is None:
            return None

        else:
            if field.valuetype in [ValueTypes.SINGLE, ValueTypes.SET, ValueTypes.LIST]:
                return self.convert_value_from_db(field, value)

            elif field.valuetype == ValueTypes.MAP:
                return json.loads(value)

    def load_all(self):
        entities = []
        for unit_meta in self.__persisted_types:
            entities.extend(self.load_type(unit_meta))

        return entities

    def load_units(self):
        entities = []
        for unit_meta in EntityTypes:
            entities.extend(self.load_type(unit_meta))

        return entities

    def load_type(self, unit_meta):
        entities = []

        if unit_meta.type_name[0] != "_":
            entities = self.load_entities(unit_meta, filters=None, conn=None)

        return entities

    def load_entities(self, meta_type, filters=None, conn=None):
        entities = {}

        close_connection = ( conn is None )
        if conn is None:
            conn = self._create_connection()

        try:
            sql_tables = self.__sql_tables(self.__table_name(meta_type), meta_type.fields_enum)

            try:
                select_sql = self.__render_tempate(self.select_template, filters, sql_table=sql_tables[0], filters=filters)

                c = self._create_cursor(conn)

                print("{} with {}".format(select_sql, filters))
                if filters:
                    values = self.create_exectute_params()
                    for f in filters:
                        self.add_execute_param(values, f[0], f[2])
                    c.execute(select_sql, values)
                else:
                    c.execute(select_sql)

                global_ids = set()

                rows = c.fetchall()
                for row in rows:
                    #print(row[0])
                    global_ids.add(row[0])
                    unit_global_id = row[1]
                    meta_type_global_id = row[2]
                    entity_id = row[3]
                    unit_entity = Store.access(Operation.GET, None, row[1])
                    meta_type_entity = Store.access(Operation.GET, None, row[2])
                    #print("{}:{}:{}".format(unit_entity, row[3], meta_type_entity))
                    entity = Store.access(Operation.GET, None, unit_entity, row[3], meta_type_entity)

                    index = 4 # 0 - global_id 1-3: base fields
                    for field in meta_type.fields_enum:
                        if not field.valuetype in [ValueTypes.LIST, ValueTypes.SET]:
                            value = self.map_value_from_db(field, row[index])
                            if not value is None:
                                entity.access(Operation.SET, value, field)

                            index += 1

                    entity.set_committed()
                    entities[row[0]] = entity
            finally:
                self._close_cursor(c)

            # Do multivalue fields
            for field in meta_type.fields_enum:
                if field.valuetype in [ValueTypes.LIST, ValueTypes.SET]:
                    multivalue_sql_table = None
                    for stbl in sql_tables:
                        if stbl.table_name == "{}_{}".format(sql_tables[0].table_name, field.name):
                            multivalue_sql_table = stbl
                            break
                    multivalue_select_sql = self.__render_tempate(self.select_template, None, sql_table=multivalue_sql_table, filters=None)
                    try:
                        c = self._create_cursor(conn)
                        #print("{}".format(multivalue_select_sql))
                        c.execute(multivalue_select_sql)
                        rows = c.fetchall()
                        for row in rows:
                            if row[0] in global_ids:
                                entities[row[0]].access(Operation.ADD, self.map_value_from_db(field, row[2]), field)
                                entities[row[0]].set_committed()

                    finally:
                        self._close_cursor(c)
        finally:
            if close_connection:
                self._close_connection(conn)

        return entities.values()


    def insert_entity(self, entity, conn=None):
        return_value = False

        close_connection = ( conn is None )
        if conn is None:
            conn = self._create_connection()

        meta_type = entity.get_meta_type_enum()
        if meta_type in self.__persisted_types:
            sql_tables = self.__sql_tables(self.__table_name(meta_type), meta_type.fields_enum)
            multivalues = {}

            insert_sql = self.__render_tempate(self.insert_into_table_template, sql_table=sql_tables[0])
            values = self.create_exectute_params()
            self.add_execute_param(values, "_global_id", entity.global_id())
            self.add_execute_param(values, "_unit", entity.unit.global_id())
            self.add_execute_param(values, "_meta_type", entity.meta_type.global_id())
            self.add_execute_param(values, "_entity_id", entity.entity_id)
            for field in meta_type.fields_enum:
                if not field.valuetype in [ValueTypes.LIST, ValueTypes.SET]:
                    self.add_execute_param(values, "_"+field.name, self.map_value_to_db(field, entity))
                else:
                    multivalue_tablename = "{}_{}".format(sql_tables[0].table_name, field.name)
                    multivalues[multivalue_tablename] = (field.name, self.map_value_to_db(field, entity))

            try:
                return_value = self.__update_entity_values(insert_sql, values, conn)
                if return_value:
                    return_value = self.__update_entity_multivalues(entity, sql_tables, multivalues, conn, need_delete=False)
            finally:
                if close_connection:
                    self._close_connection(conn)

        if return_value:
            entity.set_committed()

        return return_value

    def __update_entity_multivalues(self, entity, sql_tables, multivalues, conn, need_delete=False):
        return_value = True

        if len(sql_tables) > 1:
            for idx, sql_table in enumerate(sql_tables[1:], start=1):
                if return_value:
                    if need_delete:
                        delete_sql = self.__render_tempate(self.delete_template, sql_table=sql_table)
                        delete_values = self.create_exectute_params()
                        self.add_execute_param(delete_values, "_global_id", entity.global_id())
                        return_value = self.__update_entity_values(delete_sql, delete_values, conn)

                    if return_value:
                        field_name, multivalues_array = multivalues[sql_table.table_name]
                        if multivalues_array:
                            insert_sql = self.__render_tempate(self.insert_into_table_template, sql_table=sql_table)
                            for value_cnt, value in enumerate(multivalues_array):
                                values = self.create_exectute_params()
                                self.add_execute_param(values, "_global_id", entity.global_id())
                                self.add_execute_param(values, "_value_cnt", value_cnt)
                                self.add_execute_param(values, "_"+field_name+"_value", value)
                                return_value = self.__update_entity_values(insert_sql, values, conn)

        return return_value

    def update_entity(self, entity, conn=None):
        return_value = False

        close_connection = ( conn is None )
        if conn is None:
            conn = self._create_connection()
        meta_type = entity.get_meta_type_enum()
        if meta_type in self.__persisted_types:
            sql_tables = self.__sql_tables(self.__table_name(meta_type), meta_type.fields_enum)
            try:
                update_sql = self.__render_tempate(self.update_template, sql_table=sql_tables[0])
                values = self.create_exectute_params()
                self.add_execute_param(values, "_global_id", entity.global_id())

                multivalues = {}

                for field in meta_type.fields_enum:
                    if not field.valuetype in [ValueTypes.LIST, ValueTypes.SET]:
                        self.add_execute_param(values, "_"+field.name, self.map_value_to_db(field, entity))
                    else:
                        multivalue_tablename = "{}_{}".format(sql_tables[0].table_name, field.name)
                        multivalues[multivalue_tablename] = (field.name, self.map_value_to_db(field, entity))

                return_value = self.__update_entity_values(update_sql, values, conn)
                if return_value:
                    return_value = self.__update_entity_multivalues(entity, sql_tables, multivalues, conn, need_delete=True)

            finally:
                if close_connection:
                    self._close_connection(conn)

        if return_value:
            entity.set_committed()

        return return_value

    def __update_entity_values(self, update_sql, values, conn):
        return_value = False

        try:
            c = self._create_cursor(conn)
            #if update_sql.startswith("UPDATE"):
            #    print("Updating {} with {}".format(values, update_sql))
            c.execute(update_sql, values)

            return_value = True
        finally:
            self._close_cursor(c)

        return return_value

    def persist_entities(self, entities):
        conn = None
        try:
            conn = self._create_connection()
            for e in entities:
                if e.committed == Committed.CREATED:
                    self.insert_entity(e, conn)
                elif e.committed == Committed.UPDATED:
                    self.update_entity(e, conn)
                elif e.committed == Committed.DELETED:
                    pass
        finally:
            self._close_connection(conn)

    def __render_tempate(self, template_func, *args, **kwargs):
        try: 
            template = Template(template_func(*args))
            return template.render(**kwargs)
        except:
            traceback.print_exc()

    def __table_name(self, unit_meta):
        return "{}_{}".format(self.__unit_meta_unit[unit_meta], unit_meta.type_name)

    def __sql_tables(self, table_name, fields_enum):
        sql_tables = []
        sql_table = SqlTable(table_name)
        sql_tables.append(sql_table)
        sql_table.add_field("_global_id", self.sql_type(Datatypes.STRING, ValueTypes.SINGLE, primary_key=True), primary_key=True, base_field=True)
        for base_field in EntityTypes._entity_base.fields_enum:
            if base_field != EntityBaseMeta.committed:
                sql_table.add_field("_"+base_field.name, self.sql_type(base_field.datatype, base_field.valuetype), base_field=True)
        for field in fields_enum:
            if field.valuetype in [ValueTypes.LIST, ValueTypes.SET]:
                multivalue_sql_table = SqlTable("{}_{}".format(table_name, field.name))
                multivalue_sql_table.add_field("_global_id", self.sql_type(Datatypes.STRING, ValueTypes.SINGLE, primary_key=True), primary_key=True, base_field=True)
                multivalue_sql_table.add_field("_value_cnt", self.sql_type(Datatypes.INT, ValueTypes.SINGLE), primary_key=True, base_field=True)
                multivalue_sql_table.add_field("_"+field.name+"_value", self.sql_type(field.datatype, ValueTypes.SINGLE))
                sql_tables.append(multivalue_sql_table)
            else:
                sql_table.add_field("_"+field.name, self.sql_type(field.datatype, field.valuetype))

        return sql_tables

    def table_schemas(self, unit_meta, conn=None):
        table_schemas = []
        table_name = self.__table_name(unit_meta)
        if not self.__table_exists_internal(table_name, conn):
            sql_tables = self.__sql_tables(table_name, unit_meta.fields_enum)
            for sql_table in sql_tables:
                table_schemas.append(self.__render_tempate(self.create_table_template, sql_table, sql_table=sql_table))

        return table_schemas

    def __table_exists_internal(self, table_name, conn=None):
        if conn is None:
            try:
                conn = self._create_connection()
                self.table_exits(table_name, conn)
            finally:
                self._close_connection(conn)
        else:
            self.table_exits(table_name, conn)

    def __generate_base_schema(self, conn=None):
        self.generate_schema(UNIT_ENTITY, EntityTypes, conn)
        #self.generate_schema(UNIT_EVENTS, EventTypes, conn)

    def generate_schema(self, unit_name, unit_meta_enums, conn = None):
        close_connection = ( conn is None )
        schema = []

        if conn is None:
            conn = self._create_connection()

        try:
            for unit_meta in unit_meta_enums:
                self.__unit_meta_unit[unit_meta] = unit_name
                self.__persisted_types.add(unit_meta)
                if unit_meta.type_name[0] != "_":
                    table_name = self.__table_name(unit_meta)
                    tbl_schema_strings = self.table_schemas(unit_meta, conn)
                    for tbl_schema_string in tbl_schema_strings:
                        if not tbl_schema_string is None:
                            schema.append(tbl_schema_string)
                            self.create_table(tbl_schema_string, conn)
            if not EntityTypes.unit in self.__persisted_types:
                self.__generate_base_schema(conn)
        finally:
            if close_connection:
                self._close_connection(conn)

        for sch in schema:
            print(sch)

        return schema
