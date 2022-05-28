import responses
from cloudscale import (
    CLOUDSCALE_API_URL,
    Cloudscale,
    CloudscaleApiException,
    CloudscaleException,
)

OBJECTS_USER_RESP = {
    "href": "https://api.cloudscale.ch/v1/objects-users/6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15",
    "id": "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15",
    "display_name": "alan",
    "keys": [
        {
            "access_key": "0ZTAIBKSGYBRHQ09G11W",
            "secret_key": "bn2ufcwbIa0ARLc5CLRSlVaCfFxPHOpHmjKiH34T",
        }
    ],
    "tags": {"project": "apollo"},
}


@responses.activate
def test_objects_user_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users",
        json=[OBJECTS_USER_RESP],
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users?tag:project=apollo",
        json=[OBJECTS_USER_RESP],
        status=200,
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/objects-users", json={}, status=500
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users",
        json=[OBJECTS_USER_RESP],
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users?tag:project=apollo",
        json=[OBJECTS_USER_RESP],
        status=200,
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/objects-users", json={}, status=500
    )

    cloudscale = Cloudscale(api_token="token")
    objects_users = cloudscale.objects_user.get_all()
    assert objects_users[0]["display_name"] == "alan"
    assert (
        objects_users[0]["id"]
        == "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    )

    cloudscale = Cloudscale(api_token="token")
    objects_users = cloudscale.objects_user.get_all(filter_tag="project=apollo")
    assert objects_users[0]["display_name"] == "alan"
    assert (
        objects_users[0]["id"]
        == "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    )

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.objects_user.get_all()
    except CloudscaleApiException as e:
        assert e.status_code == 500
        assert str(e).startswith("API Response Error (500):")


@responses.activate
def test_objects_user_get_by_uuid():
    uuid = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users/" + uuid,
        json=OBJECTS_USER_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users/unknown",
        json={},
        status=404,
    )

    cloudscale = Cloudscale(api_token="token")
    objects_user = cloudscale.objects_user.get_by_uuid(uuid=uuid)
    assert objects_user["display_name"] == "alan"
    assert objects_user["id"] == uuid

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.objects_user.get_by_uuid(uuid="unknown")
    except CloudscaleApiException as e:
        assert e.status_code == 404


@responses.activate
def test_objects_user_delete():
    uuid = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users/" + uuid,
        json=OBJECTS_USER_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users/unknown",
        json=OBJECTS_USER_RESP,
        status=200,
    )
    responses.add(
        responses.DELETE, CLOUDSCALE_API_URL + "/objects-users/" + uuid, status=204
    )
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + "/objects-users/unknown",
        json={},
        status=404,
    )

    cloudscale = Cloudscale(api_token="token")
    objects_user = cloudscale.objects_user.delete(uuid=uuid)
    assert not objects_user

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.objects_user.delete(uuid="unknown")
    except CloudscaleApiException as e:
        assert e.status_code == 404


@responses.activate
def test_objects_user_create():
    display_name = "alan"

    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/objects-users",
        json=OBJECTS_USER_RESP,
        status=201,
    )
    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/objects-users", json={}, status=500
    )
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/objects-users",
        json=OBJECTS_USER_RESP,
        status=201,
    )
    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/objects-users", json={}, status=500
    )

    cloudscale = Cloudscale(api_token="token")
    cloudscale.objects_user.create(
        display_name=display_name,
    )

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.objects_user.create(
            display_name=display_name,
        )
    except CloudscaleApiException as e:
        assert e.status_code == 500


@responses.activate
def test_objects_user_update():
    uuid = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    display_name = "alan"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/objects-users/" + uuid,
        json=OBJECTS_USER_RESP,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/objects-users/" + uuid,
        json=OBJECTS_USER_RESP,
        status=200,
    )
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/objects-users/unknown",
        json={},
        status=404,
    )

    cloudscale = Cloudscale(api_token="token")
    objects_user = cloudscale.objects_user.update(uuid=uuid, display_name=display_name)
    assert objects_user["display_name"] == display_name
    assert objects_user["id"] == uuid

    try:
        cloudscale = Cloudscale(api_token="token")
        objects_user = cloudscale.objects_user.update(
            uuid="unknown", display_name=display_name
        )
    except CloudscaleApiException as e:
        assert e.status_code == 404
