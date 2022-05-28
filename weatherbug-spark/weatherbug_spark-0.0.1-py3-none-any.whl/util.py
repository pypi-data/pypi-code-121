import hmac
import time
from urllib.parse import quote
import base64


def _get_hmac_url(lat: str, lon: str) -> str:
    """Calculate HMAC required by Pulse API."""
    postdata = ""
    method = "GET"
    timestamp = round(time.time())
    secret = b"d96d6f08999c48328b5e57a9026c5c54"
    key = "LxAppV1"
    timestamp_millis = str(timestamp * 1000)

    dataToBeHashed = f"{method}\n/data/lightning/v1/spark\n{postdata}\n{timestamp}\n"
    fake_query_pairs = [
        ["isGpsLocation", "false"],
        ["location", f"{lat},{lon}"],
        ["locationtype", "latitudelongitude"],
        ["safetyMessage", "true"],
        ["shortMessage", "true"],
        ["units", "english"],
        ["verbose", "true"],
        ["_", timestamp_millis],
    ]

    fake_query_pairs.sort()

    result = "https://cmn-lx.pulse.weatherbug.net/data/lightning/v1/spark?"
    for i, pair in enumerate(fake_query_pairs):
        dataToBeHashed += pair[0] + "\n"
        result += pair[0] + "="
        dataToBeHashed += pair[1]
        result += pair[1]
        if i != len(fake_query_pairs) - 1:
            result += "&"
            dataToBeHashed += "\n"

    print(dataToBeHashed)

    hmac_hash: str = quote(
        base64.b64encode(hmac.new(secret, dataToBeHashed.encode(), "sha256").digest())
    )

    print(hmac_hash)

    final_url = result + f"&authid={key}&timestamp={timestamp}&hash={hmac_hash}"
    return final_url
