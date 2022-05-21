import re
from ..env import Environment

_alias_exp = re.compile(r"\{\{([\w_]+)\}\}")


class Base:
    class Meta:
        environ: Environment = None


class Field:
    def __init__(self, env_name=None, default=None, nullable=False, cast=lambda x: x):
        self.default = default
        self.cast = cast
        self.nullable = nullable
        self.env_name = env_name
        self.alias = None

        m = _alias_exp.match(self.env_name or "")
        if m is not None:
            self.alias = m.group(1)

    def __set_name__(self, owner: Base, name):
        assert issubclass(owner, Base), f"{owner.__name__} does not inherit {Base.__name__}"
        assert owner.Meta.environ is not None, "environ is not set on this object"

        self.field_name = name
        self.varname = self.env_name or name.upper()

    def __get__(self, obj: Base, objtype=None):
        if obj is None:
            obj = objtype

        if self.alias is not None:
            if self.alias == self.field_name:
                raise Exception(f"{self.field_name}: variable is aliased to itself")

            return getattr(obj, self.alias)

        return obj.Meta.environ.get(key=self.varname,
                                    default=self.default,
                                    nullable=self.nullable,
                                    mapper=self.cast)

    def __set__(self, obj, value):
        raise AttributeError("cannot set read-only attribute")
