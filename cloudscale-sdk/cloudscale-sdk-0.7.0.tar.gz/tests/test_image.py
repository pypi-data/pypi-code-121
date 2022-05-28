import responses
from cloudscale import (
    CLOUDSCALE_API_URL,
    Cloudscale,
    CloudscaleApiException,
    CloudscaleException,
)

IMAGE_RESP = {
    "slug": "arch-18.06",
    "name": "Arch 18.06",
    "operating_system": "Arch",
    "default_username": "arch",
    "zones": [{"slug": "rma1"}, {"slug": "lpg1"}],
}


@responses.activate
def test_image_get_all():
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/images", json=[IMAGE_RESP], status=200
    )
    responses.add(
        responses.GET, CLOUDSCALE_API_URL + "/images", json=[IMAGE_RESP], status=200
    )
    responses.add(responses.GET, CLOUDSCALE_API_URL + "/images", json={}, status=500)

    cloudscale = Cloudscale(api_token="token")
    images = cloudscale.image.get_all()
    assert images[0]["slug"] == "arch-18.06"
    assert images[0]["name"] == "Arch 18.06"
