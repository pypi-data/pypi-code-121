from abc import ABC
# from engine.exceptions import ValidationError


class BaseRule(ABC):
    # errors = None
    name = "base_rules.default"
    message = "Blank Row Found"
    severity = ''
    
    @property
    def code(self):
        if self.name:
            return self.name
        else:
            self.__class__.__name__
    
    @property
    def errors(self):
        return {
            "severity": self.severity,
            "category": self.code,
            "reason": self.message
        }
    
    def is_valid(self, item):
        if not len(item):
            return False
        return True
