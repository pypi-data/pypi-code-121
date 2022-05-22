import inspect

from pydantic import BaseModel


class Base(BaseModel):
    @classmethod
    def from_telegram_type_dict(cls, obj) -> dict:
        cls_dict = {}
        if 'owner_id' in cls.__fields__:
            cls_dict['owner_id'] = obj._client.cached_me.id
        for a, v in obj.__dict__.items():
            if a not in cls.__fields__:
                continue
            field_type = cls.__fields__[a].type_
            cls_dict[a] = ( field_type.from_telegram_type(v)
                            if inspect.isclass(field_type) and issubclass(field_type, Base)
                            else v )
        return cls_dict

    @classmethod
    def from_telegram_type(cls, obj):
        if obj is None:
            return None
        return cls(**cls.from_telegram_type_dict(obj))
