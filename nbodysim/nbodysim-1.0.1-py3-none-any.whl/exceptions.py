class AngularMomentumNotConservedException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class BodyCollisionException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class BodyEscapeException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class COMNotConservedException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class EnergyNotConservedException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class LinearMomentumNotConservedException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class SmallAdaptiveDeltaException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Figure8InitException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def check_exception(condition, exception, msg = "An exception occurred!"):
    if not condition:
        raise exception(msg)