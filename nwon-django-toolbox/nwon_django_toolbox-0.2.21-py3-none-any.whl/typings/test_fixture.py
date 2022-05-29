from nwon_django_toolbox.typings.pydantic_base_django import PydanticBaseDjango


class TestFixture(PydanticBaseDjango):
    path: str
    model_name: str
    preserve_password: bool
