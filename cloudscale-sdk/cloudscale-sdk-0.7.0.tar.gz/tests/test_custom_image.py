import unittest

import responses
from cloudscale import (
    CLOUDSCALE_API_URL,
    Cloudscale,
    CloudscaleApiException,
    CloudscaleException,
)

CUSTOM_IMAGE_RESP = {
    "href": "https://api.cloudscale.ch/v1/custom-images/11111111-1864-4608-853a-0771b6885a3a",
    "created_at": "2020-05-29T13:18:42.511407Z",
    "uuid": "11111111-1864-4608-853a-0771b6885a3a",
    "name": "my-image",
    "slug": "my-image-slug",
    "checksums": {
        "md5": "5b3a1f21cde154cfb522b582f44f1a87",
        "sha256": "5b03bcbd00b687e08791694e47d235a487c294e58ca3b1af704120123aa3f4e6",
    },
    "user_data_handling": "pass-through",
    "zones": [{"slug": "lpg1"}],
    "tags": {},
}

CUSTOM_IMAGE_IMPORT_RESP = {
    "href": "https://api.cloudscale.ch/v1/custom-images/import/11111111-1864-4608-853a-0771b6885a3a",
    "uuid": "11111111-1864-4608-853a-0771b6885a3a",
    "custom_image": {
        "href": "https://api.cloudscale.ch/v1/custom-images/11111111-1864-4608-853a-0771b6885a3a",
        "uuid": "11111111-1864-4608-853a-0771b6885a3a",
        "name": "my-image",
    },
    "url": "https://example.com/foo.raw",
    "status": "in_progress",
}


@responses.activate
def test_custom_images_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/custom-images",
        json=[CUSTOM_IMAGE_RESP],
        status=200,
    )

    cloudscale = Cloudscale(api_token="token")
    custom_images = cloudscale.custom_image.get_all()
    assert custom_images[0]["name"] == "my-image"
    assert custom_images[0]["uuid"] == "11111111-1864-4608-853a-0771b6885a3a"


@responses.activate
def test_custom_images_get_by_uuid():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/custom-images/" + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=200,
    )

    cloudscale = Cloudscale(api_token="token")
    custom_image = cloudscale.custom_image.get_by_uuid(uuid=uuid)
    assert custom_image["name"] == "my-image"
    assert custom_image["uuid"] == uuid


@responses.activate
def test_custom_images_delete():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.DELETE, CLOUDSCALE_API_URL + "/custom-images/" + uuid, status=204
    )
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + "/custom-images/unknown",
        json={"detail": "Not found."},
        status=404,
    )

    cloudscale = Cloudscale(api_token="token")
    custom_image = cloudscale.custom_image.delete(uuid=uuid)
    assert not custom_image

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.custom_image.delete(uuid="unknown")
    except CloudscaleApiException as e:
        assert e.status_code == 404


@responses.activate
def test_custom_images_import():
    name = "my-image"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/custom-images/import",
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=201,
    )

    cloudscale = Cloudscale(api_token="token")
    cloudscale.custom_image.import_by_url(
        url="https://example.com/foo.raw",
        name=name,
        slug="my-image-slug",
        user_data_handling="pass-through",
        source_format="raw",
        zones=["lpg1"],
    )


def test_custom_images_create_raise_error():
    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.custom_image.create(
            url="https://example.com/foo.raw",
            name="my-image",
            slug="my-image-slug",
            user_data_handling="pass-through",
            source_format="raw",
            zones=["lpg1"],
        )
    except NotImplementedError:
        pass
    else:
        assert False


@responses.activate
def test_custom_images_update():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    name = "my-image"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/custom-images/" + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/custom-images/" + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=200,
    )
    cloudscale = Cloudscale(api_token="token")
    custom_image = cloudscale.custom_image.update(uuid=uuid, name=name)
    assert custom_image["name"] == name
    assert custom_image["uuid"] == uuid


@responses.activate
def test_custom_image_import_status():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/custom-images/import/" + uuid,
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=200,
    )

    cloudscale = Cloudscale(api_token="token")
    custom_image = cloudscale.custom_image.get_import_by_uuid(uuid=uuid)
    assert custom_image["custom_image"]["name"] == "my-image"
    assert custom_image["uuid"] == uuid
    assert custom_image["status"] == "in_progress"
