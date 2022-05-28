import responses
from cloudscale import (
    CLOUDSCALE_API_URL,
    Cloudscale,
    CloudscaleApiException,
    CloudscaleException,
)

VOLUME_RESP = {
    "href": "https://api.cloudscale.ch/v1/volumes/2db69ba3-1864-4608-853a-0771b6885a3a",
    "created_at": "2019-05-29T13:18:42.511407Z",
    "uuid": "2db69ba3-1864-4608-853a-0771b6885a3a",
    "name": "capitano-root",
    "zone": {"slug": "lpg1"},
    "size_gb": 150,
    "type": "ssd",
    "server_uuids": ["9e1f9a7f-e8d0-4086-ad7e-fea161d7c5f7"],
    "tags": {},
}


@responses.activate
def test_volume_get_all():
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/volumes", json=[VOLUME_RESP], status=200
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/volumes", json=[VOLUME_RESP], status=200
    )
    responses.add(responses.GET, CLOUDSCALE_API_URL + "/volumes", json={}, status=500)

    cloudscale = Cloudscale(api_token="token")
    volumes = cloudscale.volume.get_all()
    assert volumes[0]["name"] == "capitano-root"
    assert volumes[0]["uuid"] == "2db69ba3-1864-4608-853a-0771b6885a3a"


@responses.activate
def test_volume_get_by_uuid():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=200,
    )

    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/volumes/" + uuid, json={}, status=500
    )

    cloudscale = Cloudscale(api_token="token")
    volume = cloudscale.volume.get_by_uuid(uuid=uuid)
    assert volume["name"] == "capitano-root"
    assert volume["uuid"] == uuid


@responses.activate
def test_volume_delete():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/unknown",
        json=VOLUME_RESP,
        status=200,
    )
    responses.add(responses.DELETE, CLOUDSCALE_API_URL + "/volumes/" + uuid, status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + "/volumes/unknown",
        json={"detail": "Not found."},
        status=404,
    )

    cloudscale = Cloudscale(api_token="token")
    volume = cloudscale.volume.delete(uuid=uuid)
    assert not volume

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.volume.delete(uuid="unknown")
    except CloudscaleApiException as e:
        assert e.status_code == 404


@responses.activate
def test_volume_create():
    name = "capitano-root"
    size_gb = 150
    server_uuids = "2db69ba3-1864-4608-853a-0771b6885a3a"

    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/volumes", json=VOLUME_RESP, status=201
    )
    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/volumes", json=VOLUME_RESP, status=201
    )
    responses.add(responses.POST, CLOUDSCALE_API_URL + "/volumes", json={}, status=500)

    cloudscale = Cloudscale(api_token="token")
    cloudscale.volume.create(
        name=name,
        server_uuids=server_uuids,
        size_gb=size_gb,
    )


@responses.activate
def test_volume_update():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    name = "capitano-root"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=200,
    )
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/" + uuid,
        json=VOLUME_RESP,
        status=200,
    )
    responses.add(
        responses.PATCH, CLOUDSCALE_API_URL + "/volumes/" + uuid, json={}, status=500
    )

    cloudscale = Cloudscale(api_token="token")
    volume = cloudscale.volume.update(uuid=uuid, name=name)
    assert volume["name"] == name
    assert volume["uuid"] == uuid


@responses.activate
def test_volume_get_by_uuid_not_found():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/volumes/unknown",
        json={"detail": "Not found."},
        status=404,
    )
    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.volume.get_by_uuid(uuid="unknown")
    except CloudscaleApiException as e:
        assert e.status_code == 404
        assert str(e) == "API Response Error (404): Not found."
        assert e.response == {"data": {"detail": "Not found."}, "status_code": 404}
