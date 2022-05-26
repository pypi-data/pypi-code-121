import factory

from sym.flow.cli.models.resource import TerraformResource


class TerraformResourceFactory(factory.Factory):
    class Meta:
        model = TerraformResource

    id = factory.Faker("uuid4")
    slug = factory.Sequence(lambda n: "resource-slug-%03d" % n)
    type = "slack"
    srn = factory.Sequence(
        lambda n: f"test_org:sym_integration:slack:resource-slug-%03d" % n
    )
