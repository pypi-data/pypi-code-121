import httpx
import xmltodict


class IrishRail:
    def _request(self, url):
        response = httpx.get(url)
        data = xmltodict.parse(response.content)
        return data

    def next_trains(self, station):
        data = self._request(f"http://api.irishrail.ie/realtime/realtime.asmx/getStationDataByNameXML?StationDesc={station}")
        data = data["ArrayOfObjStationData"]["objStationData"]
        return sorted(data, key=lambda s: s["Duein"])

    def list_stations(self):
        data = self._request("http://api.irishrail.ie/realtime/realtime.asmx/getAllStationsXML")
        data = data["ArrayOfObjStation"]["objStation"]
        return sorted(data, key=lambda s: s["StationDesc"])
