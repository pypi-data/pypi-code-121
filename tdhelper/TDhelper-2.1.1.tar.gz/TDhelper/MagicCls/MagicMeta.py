from TDhelper.generic.transformationType import transformation
from TDhelper.MagicCls.FieldsType import FieldType

class _AttributeOverride:
    def __init__(self, name, m_type):
        self._name = name
        self._type = m_type

    def __get__(self, instance, owen):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        instance.__dict__[self._name] = transformation(value, self._type)

    def __delete__(self, instance):
        instance.__dict__.pop(self._name)


class MagicMeta(type):
    def __new__(cls, name, bases, dct):
        attrs = {
            "__mapping__": {},
            "__reverse_mapping__": {},
            "__sourceOffset__": 0,
            "__instance__": __instance__,
            "__items__": [],
            "items": items,
        }
        for name, value in dct.items():
            if isinstance(dct[name], FieldType):
                try:
                    assert not attrs.__contains__(name),"field name<%s> is default attrbute, please change." % name
                    attrs["__mapping__"][name] = value.bind
                    attrs["__reverse_mapping__"][value.bind] = name
                    attrs[name] = _AttributeOverride(name, value.fieldType)
                except Exception as e:
                    raise e
            else:
                attrs[name] = value
        return super(MagicMeta, cls).__new__(cls, name, bases, attrs)


def __instance__(self):
    for n, v in self.__mapping__.items():
        setattr(self, n, self.Meta.source[self.__sourceOffset__][v])
    return self

def items(self):
    for r in self.Meta.source:
        for n, v in r.items():
            setattr(self, self.__reverse_mapping__[n], v)
        yield self
