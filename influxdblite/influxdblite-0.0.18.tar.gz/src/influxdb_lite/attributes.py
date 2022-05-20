
class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.default = kwargs.get('default', None)
        self.is_nullable = kwargs.get('is_nullable', True)
        self.value = kwargs.get('value', None)

    def validate(self, value):
        if value is None and self.default is None and not self.is_nullable:
            raise ValueError('This tag cannot be nullable')

    def set_name(self, name: str):
        if self.name is not None and self.name != name:
            raise AttributeError(f'Name duplicity: Two distinct names where given: {self.name} and {name}')
        self.name = name

    def set_value(self, value):
        self.value = value

    def __eq__(self, other):
        return self.name, '==', other

    def __gt__(self, other):
        return self.name, '>', other

    def __ge__(self, other):
        return self.name, '>=', other

    def __lt__(self, other):
        return self.name, '<', other

    def __le__(self, other):
        return self.name, '<=', other

    def in_(self, other):
        return self.name, 'in', other


class GeneralAttr:
    caster = None

    @classmethod
    def cast(cls, elem):
        if not cls.caster:
            return elem
        try:
            return cls.caster(elem)
        except ValueError:
            return elem


class Integer(GeneralAttr):
    caster = int


class Float(GeneralAttr):
    caster = float


class String(GeneralAttr):
    caster = str


class Boolean(GeneralAttr):
    caster = bool


class Tag(Base):
    def __init__(self, _type: (GeneralAttr, Integer, Float, String, Boolean) = None, **kwargs):
        super().__init__(**kwargs)
        self._type = _type

    def cast(self, elem):
        if self._type:
            return self._type.cast(elem)
        return elem


class Field(Base):
    pass


class Timestamp(Base):
    pass




