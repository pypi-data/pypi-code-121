# -*- coding: UTF-8 -*-
# Copyright 2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Usage of classproperty:
from future.utils import with_metaclass

class Dummy(with_metaclass(classproperty)):

    _name = 'Dummy'

    @classproperty.getter
    def name(cls):
        return cls._name

    @classproperty.setter('name')
    def name(cls, value):
        cls._name = value

    # Another Use Case

    def get_klass_property(*args, **kwargs):
        # Do something here
        pass

    def set_klass_property(*args, **kwargs):
        # Do something here
        pass

    klass_property = classproperty(get_klass_property, set_klass_property)

"""


from copy import copy
from types import FunctionType
from inspect import isclass

class ClassPropertyDescriptor(object):
    fget = None
    fset = None

    def __init__(self, fget, fset=None):

        if not isinstance(fget, (classmethod, staticmethod)):
            fget = classmethod(fget)
        self.fget = fget

        if fset is not None:
            self.setter(fset)

    def __get__(self, obj, cls=None):
        if cls is None:
            if isclass(obj):
                cls = obj
            else:
                cls = obj.__class__
        else:
            if not isclass(cls):
                cls = cls.__class__
        return self.fget.__get__(obj, cls)()

    def setter(self, fset):
        if not isinstance(fset, (classmethod, staticmethod)):
            fset = classmethod(fset)
        self.fset = fset

    def __set__(self, obj, value):
        if self.fset is None:
            raise Exception(f"fset of the classproperty ({self.fget.__func__.__name__}) is not defined!")
        cls = obj
        if not isclass(cls):
            cls = cls.__class__
        self.fset.__get__(obj, cls)(value)


class classproperty(type):

    PROPERTIES = dict()

    def __new__(cls, name, bases=None, attrs_dict=None):

        if isinstance(name, (classmethod, staticmethod, FunctionType)):
            fget, fset, fdel = name, bases, attrs_dict
            if fdel is not None:
                raise NotImplementedError

            cpd = ClassPropertyDescriptor(fget)
            if fset is not None:
                cpd.setter(fset)

            if isinstance(fget, (classmethod, staticmethod)):
                name = fget.__func__.__name__
            else:
                name = fget.__name__
            cls.PROPERTIES[name] = cpd
            return cpd

        for k, v in attrs_dict.items():
            if isinstance(v, ClassPropertyDescriptor):
                for key, value in cls.PROPERTIES.items():
                    if value == v:
                        delete_key = key
                        break
                del cls.PROPERTIES[delete_key]
                cls.PROPERTIES[k] = v

        to_be_set = dict()
        for b in bases:
            for base in b.__mro__:
                if type(base) not in [object, type]:
                    for k, v in base.__dict__.items():
                        if k in cls.PROPERTIES:
                            continue
                        if isinstance(v, ClassPropertyDescriptor):
                            if k in attrs_dict and not isinstance(attrs_dict[k], ClassPropertyDescriptor):
                                to_be_set[k] = attrs_dict[k]
                            cls.PROPERTIES[k] = v

        properties = copy(cls.PROPERTIES)
        attrs_dict.update(properties, PROPERTIES=properties.keys())
        cls.PROPERTIES.clear()
        new_class = super(classproperty, cls).__new__(cls, name, bases, attrs_dict)
        for k, v in to_be_set.items():
            setattr(new_class, k, v)
        return new_class

    def __getattribute__(self, attr):
        if attr == 'PROPERTIES':
            return self.__dict__['PROPERTIES']
        elif attr != '__dict__' and self == classproperty and attr in self.PROPERTIES:
            return self.PROPERTIES[attr]
        else:
            return super().__getattribute__(attr)

    def __setattr__(self, attr, value):
        if attr in self.PROPERTIES:
            self.__dict__[attr].__set__(self, value)
        else:
            super().__setattr__(attr, value)
