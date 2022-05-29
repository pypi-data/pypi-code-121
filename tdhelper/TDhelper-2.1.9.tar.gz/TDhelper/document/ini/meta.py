from TDhelper.generic.transformationType import transformation
from TDhelper.document.ini.fields import FieldType
import configparser

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


class iniMeta(type):
    def __new__(cls, name, bases, dct):
        attrs = {
            "__mapping__": {},
            "__reverse_mapping__": {},
            "__sourceOffset__": 0,
            "__instance__": __instance__,
            "__items__": []
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
        return super(iniMeta, cls).__new__(cls, name, bases, attrs)


def __instance__(self):
    conf= configparser.ConfigParser()
    conf.read(self.Meta.source,encoding="utf-8")
    for n, v in self.__mapping__.items():
        try:
            v= str.split(v,'.')
            setattr(self, n, conf.get(v[0],v[1]))
        except Exception as e:
            raise e
