import pytest
from fastapi.testclient import TestClient

from CleanEmonBackend.API import create_app

api = create_app()
client = TestClient(api)


class TestGetData:

    def test_json_date(self):
        for date in ["today", "YESTERDAY", "2022-05-01"]:
            response = client.get(f"/json/date/{date}")
            data = response.json()

            assert response.status_code == 200

            assert "date" in data
            assert type(data["date"]) is str

            assert "energy_data" in data
            assert type(data["energy_data"]) is list

    def test_json_range(self):
        response = client.get("/json/range/2022-05-01/2022-05-02")
        data = response.json()

        assert response.status_code == 200

        assert "from_date" in data
        assert "to_date" in data
        assert "range_data" in data
        assert type(data["range_data"]) is list

    @pytest.mark.projectwise
    def test_sensors(self):
        sensors = "timestamp,power,external_temp"

        response = client.get(f"/json/date/2022-05-10?sensors={sensors}")
        data = response.json()

        for sensor in sensors.split(","):
            assert sensor in data["energy_data"][0]

    def test_bad_date(self):
        for today_str in ["last_year", "20-2-3", "2020-06-34"]:

            response = client.get(f"/json/date/{today_str}")
            data = response.json()

            assert response.status_code == 400

            assert "message" in data
            assert today_str in data["message"]

    def test_bad_date_range_1(self):
        """The to_date is an invalid date"""

        to_date = "2000"

        response = client.get(f"/json/range/2022-05-01/{to_date}")
        data = response.json()

        assert response.status_code == 400

        assert "message" in data
        assert to_date in data["message"]

    def test_bad_date_range_2(self):
        """The first date is valid but the second date is valid, but in bad order."""
        to_date = "2000-01-01"

        response = client.get(f"/json/range/2022-05-01/{to_date}")
        data = response.json()

        assert response.status_code == 400

        assert "message" in data
        assert to_date in data["message"]
