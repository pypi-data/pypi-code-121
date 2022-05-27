from typing import Optional

class Configurator:
    base_url: Optional[str] = None
    bearer_token: Optional[str] = None
    options: dict = {}

    @classmethod
    def build(cls, bearer_token, base_url):
        instance = cls()
        instance.base_url = base_url
        instance.bearer_token = bearer_token
        instance.validate()
        return instance

    def validate(self) -> bool:
        assert self.base_url is not None, 'base_url не указан'
        assert self.bearer_token is not None, 'bearer token не указан'
        return True
