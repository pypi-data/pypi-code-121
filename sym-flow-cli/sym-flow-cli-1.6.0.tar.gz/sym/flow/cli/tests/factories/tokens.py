import factory

from sym.flow.cli.models.token import SymToken, SymTokenUser


class SymTokenUserFactory(factory.Factory):
    class Meta:
        model = SymTokenUser

    id = factory.Faker("uuid4")
    type = "normal"


class SymTokenFactory(factory.Factory):
    class Meta:
        model = SymToken

    identifier = factory.Faker("uuid4")
    user = factory.SubFactory(SymTokenUserFactory, type="bot")
    created_by = factory.SubFactory(SymTokenUserFactory)
    expires_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    label = factory.Faker("word")
