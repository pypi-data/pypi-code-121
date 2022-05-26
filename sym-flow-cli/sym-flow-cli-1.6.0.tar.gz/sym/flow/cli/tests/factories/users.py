import factory

from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.models.user import Identity, User
from sym.flow.cli.models.user_type import UserType


class ServiceFactory(factory.Factory):
    class Meta:
        model = Service

    id = factory.Faker("uuid4")
    label = factory.Sequence(lambda n: "Service %03d" % n)
    slug = factory.Faker("word", ext_word_list=[s.type_name for s in ServiceType])
    external_id = factory.Sequence(lambda n: "ABC-%03d" % n)


class IdentityFactory(factory.Factory):
    class Meta:
        model = Identity

    service = factory.SubFactory(ServiceFactory)
    matcher = factory.Dict({"email": "user@symops.io"})
    profile = factory.Dict(
        {"first_name": "Guinea", "last_name": "Pig", "email": "user@symops.io"}
    )


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    identities = factory.List(
        [
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.SYM.type_name,
                service__external_id="cloud",
                matcher=factory.Dict(
                    {"email": factory.Sequence(lambda n: "user-%03d@symops.io" % n)}
                ),
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.SLACK.type_name,
                service__external_id="T12345",
                matcher={"user_id": "U12345"},
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.PAGERDUTY.type_name,
                service__external_id="pytest-pd",
                matcher={"user_id": "PD123"},
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.AWS_SSO.type_name,
                service__external_id="sso-inst-arn/12345",
                matcher={
                    "principal_uuid": "1111111111-22222222-3333-4444-5555-666666666666"
                },
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.AWS_IAM.type_name,
                service__external_id="1234567890",
                matcher={"user_arn": "arn:aws:iam::838419636750:user/user@symops.io"},
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.APTIBLE.type_name,
                service__external_id="123-456-7890",
                matcher={"user_id": "123"},
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.OKTA.type_name,
                service__external_id="https://domain.okta.org",
                matcher={"user_id": "123"},
            ),
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.GITHUB.type_name,
                service__external_id="github-org-test",
                matcher={"user_id": "123"},
            ),
        ]
    )
    type = UserType.NORMAL
    created_at = factory.Faker("date_time")


class BotUserFactory(UserFactory):
    identities = factory.List(
        [
            factory.SubFactory(
                IdentityFactory,
                service__slug=ServiceType.SYM.type_name,
                service__external_id="cloud",
                matcher=factory.Dict(
                    {"username": factory.Sequence(lambda n: "botuser-%03d" % n)}
                ),
            ),
        ]
    )
    type = UserType.BOT
