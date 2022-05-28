import json
import logging
import requests

from splatnet.splatnet2.config import Config
from splatnet.splatnet2.models import Result, Results

log = logging.getLogger("splatnet.splatnet2")


class Splatnet2:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def results(self) -> Results:
        data = self._call("/api/results")
        return Results(**data)

    def result(self, battle_number: str) -> Result:
        data = self._call(f"/api/results/{battle_number}")
        return Result(**data)

    def _call(self, path: str) -> dict:
        headers = {
            "x-unique-id": "32449507786579989234",
            "x-requested-with": "XMLHttpRequest",
            "x-timezone-offset": self.config.timezone_offset(),
            "Accept-Language": self.config.language(),
            "Cookie": f"iksm_session={self.config.iksm_session()}",
        }
        log.debug("_call %s request: headers=%s", path, headers)
        response = requests.get(
            f"https://app.splatoon2.nintendo.net{path}", headers=headers
        )
        log.debug(
            "_call %s response: status=%s, headers=%s, body=%s",
            path,
            response.status_code,
            response.headers,
            response.text,
        )
        return json.loads(response.text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = Config()
    splatnet = Splatnet2(config)
    results = splatnet.results()
    print([r.battle_number for r in results.results])
    for result in results.results:
        splatnet.result(results.results[0].battle_number)
