from sym.flow.cli.models.resource import ResourceType


class TestResource:
    def test_resource_type_options(self):
        options = ResourceType.options()
        assert "sym_flow" in options
        assert "sym_error_logger" in options
