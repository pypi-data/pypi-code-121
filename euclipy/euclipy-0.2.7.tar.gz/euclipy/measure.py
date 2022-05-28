from .core import Geometry
from .registry import Registry
from .tools import pairs_in_iterable

class GeometricMeasure(Geometry):
    def __new__(cls, value=None) -> None:
        '''If value is None, then the measure is not yet quantified.
        '''
        # If value of measure is defined, then search registry for a measure of that type and value exists
        if value is not None:
            match = Registry().search_measure(cls, value)
            if match:
                return match
        # Either value is None or value has no match in Registry, so create new meesure instance
        cls.instance = super().__new__(cls)
        cls.instance._value = value
        cls.instance.measured_objects = set()
        cls.instance.label = Registry().get_auto_label(cls.instance)
        Registry().add_to_registry(cls.instance)
        return cls.instance
    
    def __repr__(self) -> str:
        return f'{self._registry_key}({self.label}={self.value})'

    def _add_measured_object(self, measured_object) -> None:
        self.measured_objects.add(measured_object)

    def set_equal_to(self, other_measure):
        if self is not other_measure:
            for measured_object in other_measure.measured_objects.union(self.measured_objects):
                measured_object.measure = self
            if self.value is not None and other_measure.value is not None and self.value != other_measure.value:
                raise ValueError
            else:
                self._value = self.value or other_measure.value
            self.measured_objects = self.measured_objects.union(other_measure.measured_objects)
            Registry().remove_from_registry(other_measure)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        if new_value is not None:
            match = Registry().search_measure(type(self), new_value)
            if match:
                match.set_equal_to(self)
                return
        self._value = new_value

class SegmentMeasure(GeometricMeasure):
    _label_prefix = 's'
    def __new__(cls, value=None) -> None:
        return super().__new__(cls, value)

class AngleMeasure(GeometricMeasure):
    _label_prefix = 'a'
    def __new__(cls, value=None) -> None:
        return super().__new__(cls, value)