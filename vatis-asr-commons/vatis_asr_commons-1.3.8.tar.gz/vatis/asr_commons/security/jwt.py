from enum import Enum


class Claim(Enum):
    LANGUAGE = 'language'
    MODEL = 'model_uid'
    SERVICE = 'service'
    USER = 'user_id'
