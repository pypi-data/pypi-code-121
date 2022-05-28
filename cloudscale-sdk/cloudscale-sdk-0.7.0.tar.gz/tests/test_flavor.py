import responses
from cloudscale import (
    CLOUDSCALE_API_URL,
    Cloudscale,
    CloudscaleApiException,
    CloudscaleException,
)

FLAVOR_RESP = {
    "slug": "flex-2",
    "name": "Flex-2",
    "vcpu_count": 1,
    "memory_gb": 2,
    "zones": [{"slug": "rma1"}, {"slug": "lpg1"}],
}


@responses.activate
def test_flavor_get_all():
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/flavors", json=[FLAVOR_RESP], status=200
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/flavors", json=[FLAVOR_RESP], status=200
    )
    responses.add(responses.GET, CLOUDSCALE_API_URL + "/flavors", json={}, status=500)

    cloudscale = Cloudscale(api_token="token")
    flavors = cloudscale.flavor.get_all()
    assert flavors[0]["slug"] == "flex-2"
    assert flavors[0]["name"] == "Flex-2"
