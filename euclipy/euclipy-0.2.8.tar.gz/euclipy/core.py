from collections import defaultdict

class Geometry:
    @classmethod
    @property
    def _registry_key(cls):
        return cls.__name__

class Theorems():
    '''Singleton registry of theorems, implemented as functions which:
        - apply the theorem if possible, and
        - return True if applied and False if not applied
    '''
    def __new__(cls):
        '''theorems is a dictionary with:
            - keys: name of the class of geometric object the theorem applies to
            - values: functions implementing theorems
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = super(Theorems, cls).__new__(cls)
            cls.instance.theorems = defaultdict(list)
        return cls.instance

    def register_theorem(self, theorem, applies_to):
        self.theorems[applies_to].append(theorem)