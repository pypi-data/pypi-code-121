from cloudam_stream.core.constants.type_constants import Types
import pickle


class Meta(dict):

    def __init__(self, description: str = "", data: dict = None):
        self.__description = description
        if data is not None:
            super(Meta, self).__init__(data)

    def set_description(self, description: str):
        self.__description = description

    def get_description(self):
        return self.__description


class FieldMeta(Meta):
    
    def __init__(self, description: str = "", data: dict = None):
        super(FieldMeta, self).__init__(description, data)


class RecordMeta(Meta):

    def __init__(self, description: str = "", data: dict = None):
        super(RecordMeta, self).__init__(description, data)


class FieldBase:

    def __init__(self, name: str, data_type: Types = Types.String):
        self.__data_type = data_type
        self.__name = name
        self.__val = None
        self.__metadata = FieldMeta()

    def get_name(self):
        return self.__name

    def get_value(self) -> object:
        return self.__val

    def set_type(self, data_type: Types):
        self.__data_type = data_type

    def get_type(self):
        return self.__data_type

    def set_name(self, name: str):
        self.__name = name

    def set_value(self, val: object):
        if type(val) is not self.get_type().value:
            raise Exception("value type error, only support " + str(self.get_type().value))
        self.__val = val
        return self

    def set_meta(self, meta: FieldMeta):
        self.__metadata = meta

    def get_meta(self) -> FieldMeta:
        return self.__metadata

    def set_meta_description(self, description: str):
        self.__metadata.set_description(description)

    def get_meta_description(self):
        return self.__metadata.get_description()

    def set_meta_attr(self, key: str, val: object):
        self.__metadata[key] = val

    def get_meta_attr(self, key):
        return self.__metadata.get(key)


class Field(FieldBase):

    def __init__(self, name: str, data_type: Types = Types.String):
        super(Field, self).__init__(name, data_type)

    def get_type_value(self):
        return super(Field, self).get_type().value


# payload 结构
class Record:

    def __init__(self, log: str = None, meta: RecordMeta = None):
        self.__fields = dict
        self.__log = log
        self.__meta = meta

    def contains_field(self, name: str) -> bool:
        return self.__fields.__contains__(name)

    def add_field(self, field: Field):
        self.__fields.update({field.get_name(): field})

    def get_field(self, name: str) -> Field:
        return self.__fields.get(name)

    def fields(self):
        return self.__fields.values()

    def remove_field(self, name: str):
        del self.__fields[name]

    def empty(self):
        self.__fields.clear()

    def set_log(self, log: str):
        self.__log = log

    def get_log(self):
        return self.__log

    def set_meta(self, meta: RecordMeta):
        self.__meta = meta

    def get_meta(self) -> RecordMeta:
        return self.__meta

    def set_meta_description(self, description: str):
        self.__meta.set_description(description)

    def get_meta_description(self) -> str:
        return self.__meta.get_description()

    def set_meta_attr(self, key: str, val: object):
        self.__meta[key] = val

    def get_meta_attr(self, key):
        return self.__meta.get(key)


# 消息体结构
class Message(object):

    def __init__(self, payload, flag=0, data_type=None):
        self.__payload = payload
        self.__flag = flag
        self.__data_type = data_type

    def serialize(self):
        return pickle.dumps(self)

    def deserialize(self):
        return pickle.loads(self)

    def set_payload(self, payload: object):
        self.__payload = payload

    def get_payload(self):
        return self.__payload

    def set_data_type(self, data_type):
        self.__data_type = data_type

    def get_data_type(self):
        return self.__data_type

