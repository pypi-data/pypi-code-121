"""List and filtered list model."""
from __future__ import annotations

# standard libraries
import collections.abc
import copy
import typing

# third party libraries
# None

# local libraries
from nion.utils import Event
from nion.utils import Observable
from nion.utils import Model
from nion.utils import ListModel
from nion.utils.ReferenceCounting import weak_partial


# TODO: logical types: datetime, timestamp, uuid, etc.
# TODO: object references (w/ content changed, delete, etc.)


MDescription = typing.Union[str, typing.Dict[str, typing.Any]]  # when napolean works: typing.NewType("MDescription", typing.Dict)
MFields = typing.List[MDescription]  # when napolean works: typing.NewType("MFields", typing.List)
DictValue = typing.Optional[typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any], typing.Tuple[typing.Any], str, int]]


STRING = "string"
BOOLEAN = "boolean"
INT = "int"
FLOAT = "double"


def define_string() -> MDescription:
    return "string"


def define_boolean() -> MDescription:
    return "boolean"


def define_int() -> MDescription:
    return "int"


def define_float() -> MDescription:
    return "double"


def define_field(name: str, type: MDescription, *, default: typing.Optional[typing.Any] = None) -> MDescription:
    d: typing.Dict[str, typing.Any] = {"name": name, "type": type}
    if default is not None:
        d["default"] = default
    return d


def define_record(name: str, fields: MFields) -> MDescription:
    return {"type": "record", "name": name, "fields": fields}


def define_array(items: MDescription) -> MDescription:
    return {"type": "array", "items": items}


class ModelLike(Observable.ObservableLike, typing.Protocol):
    field_value_changed_event: Event.Event
    array_item_inserted_event: Event.Event
    array_item_removed_event: Event.Event
    model_changed_event: Event.Event

    @property
    def field_value(self) -> typing.Any: raise NotImplementedError()

    def from_dict_value(self, value: DictValue) -> None: ...
    def to_dict_value(self) -> DictValue: ...

    def copy_from(self, m: typing.Any) -> typing.Any: raise NotImplementedError()


def build_model(schema: MDescription, *, default_value: typing.Optional[typing.Any] = None,
                value: typing.Optional[typing.Any] = None) -> ModelLike:
    if schema in ("string", "boolean", "int", "double"):
        return FieldPropertyModel(default_value if default_value is not None else value)
    type = typing.cast(typing.Dict[str, typing.Any], schema).get("type")
    if type in ("string", "boolean", "int", "double"):
        return FieldPropertyModel(default_value if default_value is not None else value)
    elif type == "record":
        record_values = copy.copy(default_value or dict())
        record_values.update(value or dict())
        return RecordModel(schema, values=record_values)
    elif type == "array":
        return ArrayModel(schema, value if value is not None else default_value)
    raise Exception(f"{type} not found.")


def build_value(schema: MDescription, *, value: typing.Optional[typing.Any]=None) -> typing.Union[typing.Any, ModelLike]:
    if schema in ("string", "boolean", "int", "double"):
        return value
    type = typing.cast(typing.Dict[str, typing.Any], schema).get("type")
    if type in ("string", "boolean", "int", "double"):
        return value
    elif type == "record":
        return RecordModel(schema, values=value)
    elif type == "array":
        return ArrayModel(schema, value)
    raise Exception(f"{type} not found.")


class FieldPropertyModel(Model.PropertyModel[typing.Any]):

    def __init__(self, value: typing.Optional[typing.Any]) -> None:
        super().__init__(value=value)
        self.field_value_changed_event = Event.Event()
        self.array_item_inserted_event = Event.Event()
        self.array_item_removed_event = Event.Event()
        self.model_changed_event = Event.Event()

    def from_dict_value(self, value: DictValue) -> None:
        self.value = value

    def to_dict_value(self) -> DictValue:
        if self.value is not None:
            return typing.cast(DictValue, self.value)
        return None

    def copy_from(self, m: typing.Any) -> typing.Any: raise NotImplementedError()

    @property
    def field_value(self) -> typing.Optional[typing.Any]:
        return self.value

    def notify_property_changed(self, key: str) -> None:
        super().notify_property_changed(key)
        self.field_value_changed_event.fire(key)
        self.model_changed_event.fire()


class RecordModel(Observable.Observable):

    __initialized = False

    def __init__(self, schema: MDescription, *, values: typing.Optional[typing.Dict[str, typing.Any]] = None):
        super().__init__()
        self.field_value_changed_event = Event.Event()
        self.array_item_inserted_event = Event.Event()
        self.array_item_removed_event = Event.Event()
        self.model_changed_event = Event.Event()
        self.__field_models = dict()
        self.__field_model_property_changed_listeners = dict()
        self.__field_model_changed_listeners = dict()
        self.__array_item_inserted_listeners = dict()
        self.__array_item_removed_listeners = dict()
        self.schema = schema
        self.item_names: typing.List[str] = list()
        self.relationship_names: typing.List[str] = list()
        assert isinstance(schema, dict)
        for field_schema in schema["fields"]:
            field_name = field_schema["name"]
            field_type = field_schema["type"]
            field_default = field_schema.get("default")
            field_model = build_model(field_type, default_value=field_default, value=(values or dict()).get(field_name))

            if isinstance(field_model, RecordModel):
                self.item_names.append(field_name)
            elif isinstance(field_model, ArrayModel):
                self.relationship_names.append(field_name)

            self.__field_models[field_name] = field_model

            def handle_property_changed(model: RecordModel, field_name: str, name: str) -> None:
                if name == "value":
                    model.property_changed_event.fire(field_name)

            def handle_array_item_inserted(model: RecordModel, field_name: str, key: str, value: typing.Any, before_index: int) -> None:
                if key == "items":
                    model.item_inserted_event.fire(field_name, value, before_index)

            def handle_array_item_removed(model: RecordModel, field_name: str, key: str, value: typing.Any, index: int) -> None:
                if key == "items":
                    model.item_removed_event.fire(field_name, value, index)

            self.__field_model_property_changed_listeners[field_name] = field_model.field_value_changed_event.listen(weak_partial(handle_property_changed, self, field_name))
            self.__field_model_changed_listeners[field_name] = field_model.model_changed_event.listen(self.model_changed_event.fire)
            self.__array_item_inserted_listeners[field_name] = field_model.array_item_inserted_event.listen(weak_partial(handle_array_item_inserted, self, field_name))
            self.__array_item_removed_listeners[field_name] = field_model.array_item_removed_event.listen(weak_partial(handle_array_item_removed, self, field_name))
        self.__initialized = True

    def close(self) -> None:
        pass

    def __deepcopy__(self, memo: typing.Dict[typing.Any, typing.Any]) -> RecordModel:
        values = self.to_dict_value()
        # assert isinstance(values, dict)
        return RecordModel(copy.deepcopy(self.schema), values=typing.cast(typing.Dict[str, typing.Any], values))

    def copy_from(self, record: RecordModel) -> None:
        self.from_dict_value(record.to_dict_value())

    def from_dict_value(self, values: DictValue) -> None:
        for k, v in self.__field_models.items():
            # assert isinstance(values, dict)
            values_dict = typing.cast(typing.Dict[str, typing.Any], values)
            if k in values_dict:
                value = values_dict[k]
                self.__field_models[k].from_dict_value(value)

    def to_dict_value(self) -> DictValue:
        d = dict()
        assert isinstance(self.schema, dict)
        for field_schema in self.schema["fields"]:
            field_name = field_schema["name"]
            field_value = self.__field_models[field_name].to_dict_value()
            if field_value is not None:
                d[field_name] = field_value
        return d

    def __getattr__(self, name: str) -> typing.Any:
        if name in self.__field_models:
            return self.__field_models[name].field_value
        if name.endswith("_model") and name[:-6] in self.__field_models:
            return self.__field_models[name[:-6]]
        raise AttributeError(f"no attribute {name} on {self}")

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if self.__initialized and name in self.__field_models and isinstance(self.__field_models[name], FieldPropertyModel):
            typing.cast(typing.Any, self.__field_models[name]).value = value
        else:
            super().__setattr__(name, value)

    @property
    def field_value(self) -> RecordModel:
        return self

    def insert_item(self, name: str, index: int, item: typing.Any) -> None:
        items = getattr(self, name)
        items.insert(index, item)

    def remove_item(self, name: str, item: typing.Any) -> None:
        items = getattr(self, name)
        del items[items.index(item)]


class ItemsSequence(collections.abc.MutableSequence):  # type: ignore

    def __init__(self, list_model: ListModel.ListModel[typing.Any]) -> None:
        super().__init__()
        self.__list_model = list_model

    def __len__(self) -> int:
        return len(self.__list_model.items)

    def __getitem__(self, key: typing.Any) -> typing.Any:
        return self.__list_model.items[key]

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        raise IndexError()

    def __delitem__(self, key: typing.Any) -> None:
        self.__list_model.remove_item(key)

    def __contains__(self, item: typing.Any) -> bool:
        return item in self.__list_model.items

    def insert(self, index: int, value: typing.Any) -> None:
        self.__list_model.insert_item(index, value)


class ArrayModel(ListModel.ListModel[typing.Any]):

    def __init__(self, schema: MDescription, values: typing.Optional[typing.List[typing.Any]] = None) -> None:
        if values is not None:
            items: typing.Optional[typing.List[typing.Any]] = list()
            assert isinstance(schema, dict)
            assert isinstance(items, list)
            item_schema = schema["items"]
            for value in values:
                items.append(build_value(item_schema, value=value))
        else:
            items = None
        super().__init__(items=items)
        self.schema = schema
        self.field_value_changed_event = Event.Event()
        self.array_item_inserted_event = Event.Event()
        self.array_item_removed_event = Event.Event()
        self.model_changed_event = Event.Event()
        self.__model_changed_listeners = list()
        for item in self.items:
            trampoline = None
            if isinstance(item, (RecordModel, ArrayModel)):
                trampoline = item.model_changed_event.listen(self.model_changed_event.fire)
            self.__model_changed_listeners.append(trampoline)

    def __deepcopy__(self, memo: typing.Dict[typing.Any, typing.Any]) -> ArrayModel:
        values = typing.cast(typing.Sequence[typing.Any], self.to_dict_value())
        # assert isinstance(values, list) or isinstance(values, tuple)
        return ArrayModel(copy.deepcopy(self.schema), values=list(values))

    def copy_from(self, array: ArrayModel) -> None:
        self.from_dict_value(array.to_dict_value())

    def from_dict_value(self, values: DictValue) -> None:
        # assert isinstance(values, list) or isinstance(values, tuple)
        values_list = typing.cast(typing.Sequence[typing.Any], values)
        while len(values_list) > len(self._items):
            assert isinstance(self.schema, dict)
            item_schema = self.schema["items"]
            self._items.append(build_value(item_schema))
        while len(values_list) < len(self._items):
            del self._items[-1]
        for value, item in zip(values_list, self._items):
            item.from_dict_value(value)

    def to_dict_value(self) -> DictValue:
        l = list()
        for item in self.items:
            l.append(item.to_dict_value())
        return l

    @property
    def field_value(self) -> ItemsSequence:
        return ItemsSequence(self)

    def notify_insert_item(self, key: str, value: typing.Any, before_index: int) -> None:
        super().notify_insert_item(key, value, before_index)
        self.array_item_inserted_event.fire(key, value, before_index)
        trampoline = None
        if isinstance(value, (RecordModel, ArrayModel)):
            trampoline = value.model_changed_event.listen(self.model_changed_event.fire)
        self.__model_changed_listeners.append(trampoline)
        self.model_changed_event.fire()

    def notify_remove_item(self, key: str, value: typing.Any, index: int) -> None:
        super().notify_remove_item(key, value, index)
        self.__model_changed_listeners.pop(index)
        self.array_item_removed_event.fire(key, value, index)
        self.model_changed_event.fire()
