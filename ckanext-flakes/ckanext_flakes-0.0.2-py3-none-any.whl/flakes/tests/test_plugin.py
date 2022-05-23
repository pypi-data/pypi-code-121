import ckan.lib.plugins as p
import pytest


@pytest.mark.ckan_config("ckan.plugins", "flakes scheming_datasets")
@pytest.mark.usefixtures("with_plugins")
def test_schema():
    context = {}
    data_dict = {"type": "camel-photos"}
    plugin = p.lookup_package_plugin()
    schema = plugin.create_package_schema()
    data, errors = p.plugin_validate(
        plugin, context, data_dict, schema, "package_create"
    )

    assert data and errors
