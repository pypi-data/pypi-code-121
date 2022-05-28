from collections import defaultdict

class Registry:
    '''Singleton registry of Geometry instances (GeometricObjects and GeometricMeasures).
    '''
    def __new__(cls):
        '''entries is a dictionary with:
            - keys: registry key
            - values: dictionaries mapping entry labels to registered entries
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = super(Registry, cls).__new__(cls)
            cls.instance.entries = defaultdict(dict)
            cls.instance.auto_label_counter = defaultdict(int)
        return cls.instance
   
    def add_to_registry(self, entry):
        self.entries[entry._registry_key][entry.label] = entry
    
    def remove_from_registry(self, entry):
        self.entries[entry._registry_key].pop(entry.label, None)

    def get_auto_label(self, geometry):
        self.auto_label_counter[geometry._registry_key] += 1
        return f'{geometry._label_prefix}{self.auto_label_counter[geometry._registry_key]}'

    def search_registry(self, registry_key, label):
        try:
            return self.entries[registry_key][label]
        except KeyError:
            return None

    def search_measure(self, measure_cls, value):
        try:
            return [m for m in self.entries[measure_cls._registry_key].values() if m.value == value][0]
        except IndexError:
            return None

    def search_polygon(self, registry_key, points: list):
        '''Find polygon that shares points, regardless of point order
        '''
        try:
            matches = [p for p in iter(self.entries[registry_key].values()) if set(p.points) == set(points)]
            return matches[0] if matches else None
        except KeyError:
            return None