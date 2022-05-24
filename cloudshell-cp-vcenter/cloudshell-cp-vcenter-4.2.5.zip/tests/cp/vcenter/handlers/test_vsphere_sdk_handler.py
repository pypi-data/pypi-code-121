from unittest.mock import Mock

from cloudshell.cp.vcenter.handlers.vsphere_api_handler import TagAlreadyExists
from cloudshell.cp.vcenter.handlers.vsphere_sdk_handler import VSphereSDKHandler


def test_tag_was_deleted_while_we_searching_for_it(logger):
    # - try to create a tag - get the error that it exists
    # - try to get it - get the error that we can't find it
    #   (it can be deleted in another thread or even Shell's venv)
    # - try to create the tag one more time
    client = Mock(
        create_tag=Mock(
            side_effect=(TagAlreadyExists("tag name", "category_id"), "tag_id")
        ),
        get_all_category_tags=Mock(side_effect=([], "tag_id")),
        get_tag_info=Mock(side_effect=({"name": "tag name", "id": "tag_id"},)),
    )

    handler = VSphereSDKHandler(client, None, logger)
    assert handler._get_or_create_tag("tag_name", "category_id") == "tag_id"
