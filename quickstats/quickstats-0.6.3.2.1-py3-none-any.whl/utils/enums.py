from enum import Enum

class GeneralEnum(Enum):
    @classmethod
    def parse(cls, expr:str):
        if isinstance(expr, cls):
            return expr
        _expr = expr.strip().upper()
        if _expr in cls.__members__:
            return cls[_expr]
        else:
            options = cls.get_members()
            raise RuntimeError(f"invalid option: {expr} (allowed options: {', '.join(options)})")
    @classmethod
    def get_members(cls):
        return [i.lower() for i in cls.__members__]
    
    
class DescriptiveEnum(GeneralEnum):
    def __init__(self, enum_id:int, description:str=""):
        self.enum_id = enum_id
        self.description = description