import responses
from cloudscale import CLOUDSCALE_API_URL, Cloudscale, CloudscaleApiException

SUBNET_RESP = {
    "href": "https://api.cloudscale.ch/v1/subnets/33333333-1864-4608-853a-0771b6885a3a",
    "uuid": "33333333-1864-4608-853a-0771b6885a3a",
    "cidr": "192.0.2.123/24",
    "network": {
        "href": "https://api.cloudscale.ch/v1/networks/2db69ba3-1864-4608-853a-0771b6885a3a",
        "uuid": "2db69ba3-1864-4608-853a-0771b6885a3a",
        "name": "my-network-name",
    },
    "gateway_address": None,
    "dns_servers": ["185.79.232.101", "185.79.232.102"],
    "tags": {},
}


@responses.activate
def test_subnet_get_all():
    uuid = "33333333-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/subnets", json=[SUBNET_RESP], status=200
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/subnets", json=[SUBNET_RESP], status=200
    )
    responses.add(responses.GET, CLOUDSCALE_API_URL + "/subnets", json={}, status=500)

    cloudscale = Cloudscale(api_token="token")
    subnets = cloudscale.subnet.get_all()
    assert subnets[0]["uuid"] == uuid


@responses.activate
def test_subnet_get_by_uuid():
    uuid = "33333333-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=200,
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/subnets/" + uuid, json={}, status=500
    )

    cloudscale = Cloudscale(api_token="token")
    subnet = cloudscale.subnet.get_by_uuid(uuid=uuid)
    assert subnet["uuid"] == uuid


@responses.activate
def test_subnet_delete():
    uuid = "33333333-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/subnets/unknown",
        json=SUBNET_RESP,
        status=200,
    )
    responses.add(responses.DELETE, CLOUDSCALE_API_URL + "/subnets/" + uuid, status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + "/subnets/unknown",
        json={"detail": "Not found."},
        status=404,
    )

    cloudscale = Cloudscale(api_token="token")
    subnet = cloudscale.subnet.delete(uuid=uuid)
    assert not subnet

    try:
        cloudscale = Cloudscale(api_token="token")
        cloudscale.subnet.delete(uuid="unknown")
    except CloudscaleApiException as e:
        assert e.status_code == 404


@responses.activate
def test_subnet_create():
    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/subnets", json=SUBNET_RESP, status=201
    )
    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/subnets", json=SUBNET_RESP, status=201
    )
    responses.add(
        responses.POST, CLOUDSCALE_API_URL + "/subnets", json=SUBNET_RESP, status=500
    )

    cloudscale = Cloudscale(api_token="token")
    cloudscale.subnet.create(
        cidr="192.0.2.123/24",
        network_uuid="2db69ba3-1864-4608-853a-0771b6885a3a",
        dns_servers=["185.79.232.101", "185.79.232.102"],
    )


@responses.activate
def test_subnet_update():
    uuid = "33333333-1864-4608-853a-0771b6885a3a"
    dns_servers = ["185.79.232.101", "185.79.232.102"]

    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=200,
    )
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/subnets/" + uuid,
        json=SUBNET_RESP,
        status=200,
    )
    responses.add(
        responses.PATCH, CLOUDSCALE_API_URL + "/subnets/" + uuid, json={}, status=500
    )
    cloudscale = Cloudscale(api_token="token")
    subnet = cloudscale.subnet.update(uuid=uuid, dns_servers=dns_servers)
    assert subnet["uuid"] == uuid
    assert subnet["dns_servers"] == dns_servers
