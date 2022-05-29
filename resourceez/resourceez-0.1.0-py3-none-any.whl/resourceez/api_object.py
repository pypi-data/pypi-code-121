"""
This was motivated by wanting to express REST resources when writing API clients in a way
that emulates the good parts of the declarative style of DRF serializers to some degree.

Since the use case here is the client side, we don't need all the type mapping and validation
functionality, so it can be way simpler and less visually noisy to define an api spec. It should
also be fast to write the code too since there's almost no boilerplate.

Extensions of the base class are intended to be composed together. To tell the parent resource
that any of its properties are sub-resources (or collections of them), you can specify the assignment
of sub-resource type to property name in a class level dict on the parent called sub_resources (see
example below). This will pass the raw value for each property to the corresponding constructor
and assign the result to the custom ApiResource field.

----


Usage
----

An example of the kind of use case that motivated this module:


    >>> resource_dict = {
    ...     "field": 1,
    ...     "list_field": [1, 2, 3],
    ...     "subresource": {
    ...         "foo": "bar"
    ...     },
    ...     "subresource_collection": [
    ...         {"foo": "baz"},
    ...         {"foo": None},
    ...     ],
    ... }

----

We have two identifiable object schemas here:

1.  The subresource:

    >>> class SubResource(ApiObject):
    ...     foo: Optional[str]

2. The top level resource:

    >>> class Resource(ApiObject):
    ...     sub_resources = {
    ...         "subresource": SubResource.parse,
    ...         "subresource_collection": SubResource.parse_collection,
    ...     }
    ...
    ...     field: int
    ...     list_field: List[int]
    ...     subresource: SubResource
    ...     subresource_collection: List[SubResource]

----

Once we define the resources and tell them if there's any nesting using the sub_resources dict, we can parse
a resource into a typehinted python object recursively.

    >>> resource = Resource.parse(resource_dict)

The parsed resource behaves exactly as you would expect the pyhton object equivalent of a dict to behave
with the added bonus of respecting the types of sub-resources and lists.

An important caveat is that this doesn't support parsing arbitrary python types, just the types that
come from json.load.

    >>> isinstance(resource.field, int)
    'True'
    >>> isinstance(resource.subresource, SubResource)
    'True'
    >>> isinstance(resource.subresource_collection[0], SubResource)
    'True'


We can also recursively turn it back into its original dict form using the raw property:


    >>> resource.raw == resource_dict
    'True'

Using this to express the API resources that a client is interacting with will hopfully
mean that we don't have to go and re-read the corresponding API docs again each time the use case changes slightly!

NOTE: This is built to be pretty tolerant, i.e. you only have to declare the parts of the resource you care about.
The other fields will be accessible as properties from the ApiObject instance that represents the parsed dict.
However, if you make use of them without declaring them in the resource definition, they won't be suggested by your
IDE's autocomplete and any type inference/static analysis will just have to trust that you know what you're doing.
"""

from __future__ import annotations

import inspect
from enum import Enum
from typing import Callable, Dict, List, TypeVar, Union, Type, Optional, Any

Primitive = Union[str, int, float, bool, None]
JsonType = Union[dict, List, Primitive]


def _trivial_constructor(raw: JsonType) -> JsonType:
    """
    Exists because writing lambda x: x inline would be less explicit. This is
    the default function used as the constructor when a subresource constructor
    isn't configured.
    :param raw:
    :return:
    """
    return raw


class ApiObject:
    sub_resources: Dict[str, _ResourceConstructor] = {}

    def __init__(self, *_, **kwargs):
        if kwargs:
            self.__dict__ = self.parse(kwargs).__dict__

    @classmethod
    def _get_subresource_constructor(cls, key: str) -> _ResourceConstructor:
        """
        When given a string key, will return a constructor function if it is specified in the subresource
        constructors, or will return a function that is basically lambda x: x if no subresource constructor
        was specified.
        :param key:
        :return:
        """
        subresource_constructor = cls.sub_resources.get(key, _trivial_constructor)

        return subresource_constructor

    @classmethod
    def parse(cls, raw: JsonType) -> Union[List[ApiObject], ApiObject, Primitive]:
        """
        The intended way to instantiate ApiResource instances. Should respect the subresource constructors
        configured in the class definition, passing the value of that dict key to the function specified.
        :param raw:
        :return:
        """
        if not isinstance(raw, JsonType.__args__):
            raise TypeError(
                f"Api resources must be composed of the following types: {JsonType.__args__}, "
                f"{type(raw)} was supplied."
            )

        if isinstance(raw, Primitive.__args__):
            return raw

        if isinstance(raw, list):
            return cls.parse_collection(raw)

        if isinstance(raw, dict):
            resource_content = []
            for key, value in raw.items():
                parsed = cls._get_subresource_constructor(key)(value)
                resource_content.append((key, parsed))
            instance = cls()
            instance.__dict__ = dict(resource_content)
            return instance

    @classmethod
    def parse_collection(
            cls, collection: List[JsonType]
    ) -> List[Union[ApiObject, Primitive]]:
        """
        Convenience function for cases where a resource has a property which is a collection of
        sub-resources with a set schema.
        :param collection:
        :return:
        """
        return [cls.parse(item) for item in collection]

    @staticmethod
    def _collection_to_raw(
            collection: List[Union[JsonType, ApiObject]]
    ) -> List[JsonType]:
        """
        Handles recursively casting lists of items to their respective JsonType
        :param collection:
        :return:
        """
        raw_collection: list = [None for _ in collection]
        for index, item in enumerate(collection):
            if isinstance(item, ApiObject):
                raw_collection[index] = item.raw
            elif isinstance(item, list):
                raw_collection[index] = ApiObject._collection_to_raw(item)
            else:
                raw_collection[index] = item

        return raw_collection

    @property
    def raw(self) -> dict:
        """
        Returns a dict that should satisfy the following constraint:
            >>> resource_dict = {...}
            >>> ApiObject.parse(resource_dict).raw == resource_dict

        Recursively converts all of its properties to their original
        json type.
        :return:
        """
        raw = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ApiObject):
                raw[key] = value.raw
            elif isinstance(value, list):
                raw[key] = self._collection_to_raw(value)
            elif isinstance(value, Enum):
                raw[key] = value.value
            else:
                raw[key] = value

        return raw


_ResourceConstructor = Callable[
    [JsonType], Union[List[ApiObject], ApiObject, Primitive]
]
RestResource = TypeVar("RestResource", bound=ApiObject)
ErrorSchema = TypeVar("ErrorSchema", bound=ApiObject)


def from_annotations(cls: Type[RestResource]) -> Type[RestResource]:
    """
    Allows the subresource parsers to be inferred from the annotations
    on the class. This means you can define your object graph as follows.

    With a resource with the following schema:

        >>> resource_dict = {
        ...     "field": 1,
        ...     "list_field": [1, 2, 3],
        ...     "subresource": {
        ...         "foo": "bar"
        ...     },
        ...     "subresource_collection": [
        ...         {"foo": "baz"},
        ...         {"foo": None},
        ...     ],
        ... }


    The resource defintions look like:

    The subresource:
        >>> class SubResource(ApiObject):
        ...     foo: str
        ...

    The top level resource:
        >>> @from_annotations
        ... class Resource(ApiObject):
        ...     field: int
        ...     list_field: List[int]
        ...     subresource: SubResource
        ...     subresource_collection: List[SubResource]


    :param cls: The ApiObject subclass
    :return:
    """
    annotations_ = cls.__annotations__

    if {str} == {type(a) for a in annotations_}:
        # If the type of every value in the __annotations__ dict is string,
        # then we're looking at a __future__.annotations import at the top
        # of the file
        annotations_ = inspect.get_annotations(cls, eval_str=True)

    for name, field_type in annotations_.items():
        is_from_typing = isinstance(field_type, type(List[Any]))

        if field_type in Primitive.__args__:
            # If the annotation is a primitive then the constructor is
            # just the default trivial constructor.
            pass

        elif (
                is_from_typing
                and field_type.__args__[0] in Primitive.__args__
        ):
            # If the annotation is a List[str] or some other primitive
            # then the constructor is just the trivial constructor.
            pass

        elif (
                is_from_typing
                and issubclass(field_type.__args__[0], ApiObject)
        ):
            # If the annotation is a typing.List[ApiResource]
            # we want to pull out the specific subclass that
            # was annotated and set the subresource constructor
            # to be its parse function.
            cls.sub_resources[name] = field_type.__args__[0].parse

        elif isinstance(field_type, type(Optional[Any])):
            # Since subresources aren't going to be typehinted as Optional,
            # we can assume that the passed type is primitive
            cls.sub_resources[name] = field_type.__args__[0]

        elif isinstance(field_type(), ApiObject):
            # If the annotation is an instance of ApiObject we
            # want to set the subresource constructor to its parse
            # function
            cls.sub_resources[name] = field_type.parse

    return cls
