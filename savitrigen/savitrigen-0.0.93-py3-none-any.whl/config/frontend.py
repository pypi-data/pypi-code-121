from dataclasses import dataclass

@dataclass
class FrontendConfig(object):
    meta:dict
    entities:list[str]

    plugins:list[str] = None

    notice:str = None
    signin_text:str = None

    has_releases:bool = False
    has_feedback:bool = False
    has_notification:bool = False
