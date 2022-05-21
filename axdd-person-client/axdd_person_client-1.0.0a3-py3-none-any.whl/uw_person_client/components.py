# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from copy import copy


class AbstractBase():

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"Attribute '{name}' does not exist on "
                                 f"'{type(self).__name__}' instance.")

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def to_dict(self):

        def format(value):
            if isinstance(value, AbstractBase):
                return value.to_dict()
            elif isinstance(value, list):
                return [format(item) for item in value]
            else:
                return value

        data = copy(self.__dict__)
        for key, value in data.items():
            data[key] = format(value)
        return data

    def to_json(self):
        return json.dumps(self.to_dict(),
                          sort_keys=True,
                          indent=2,
                          default=str)

    def from_dict(self, data, obj=None):
        if obj is None:
            obj = self
        for key, value in data.items():
            if isinstance(value, dict):
                if key == "employee":
                    new_obj = Employee()
                    obj.employee = new_obj.from_dict(value, obj=new_obj)
                elif key == "adviser":
                    new_obj = Adviser()
                    obj.adviser = new_obj.from_dict(value, obj=new_obj)
                elif key == "student":
                    new_obj = Student()
                    obj.student = new_obj.from_dict(value, obj=new_obj)
                elif key == "tran_term":
                    new_obj = Term()
                    obj.tran_term = new_obj.from_dict(value, obj=new_obj)
                elif key == "leave_ends_term":
                    new_obj = Term()
                    obj.leave_ends_term = new_obj.from_dict(value, obj=new_obj)
            elif isinstance(value, list):
                if key == "majors":
                    obj_cls = Major
                elif key == "advisers":
                    obj_cls = Adviser
                elif key == "transcripts":
                    obj_cls = Transcript
                elif key == "sports":
                    obj_cls = Sport
                items = []
                for list_value in value:
                    if isinstance(list_value, dict):
                        new_obj = obj_cls()
                        items.append(
                            new_obj.from_dict(list_value, obj=new_obj))
                    else:
                        items.append(list_value)
                obj.__setattr__(key, items)
            else:
                obj.__setattr__(key, value)
        return obj


class Person(AbstractBase):
    pass


class Student(AbstractBase):
    pass


class Employee(AbstractBase):
    pass


class Transcript(AbstractBase):
    pass


class Major(AbstractBase):
    pass


class Sport(AbstractBase):
    pass


class Adviser(AbstractBase):
    pass


class Term(AbstractBase):
    pass
