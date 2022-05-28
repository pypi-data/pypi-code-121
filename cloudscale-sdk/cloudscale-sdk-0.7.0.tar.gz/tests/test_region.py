from cloudscale import Cloudscale, CloudscaleApiException, CloudscaleException, CLOUDSCALE_API_URL
import responses

REGION_RESP = {
    "slug": "rma",
    "zones": [
        {
            "slug": "rma1"
        }
    ]
}


@responses.activate
def test_region_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/regions',
        json=[REGION_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/regions',
        json=[REGION_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/regions',
        json={},
        status=500)
    cloudscale = Cloudscale(api_token="token")
    regions = cloudscale.region.get_all()
    assert regions[0]['slug'] == "rma"
