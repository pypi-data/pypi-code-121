import pytest
from fastapi.testclient import TestClient

from CleanEmonBackend.API import create_app

api = create_app()
client = TestClient(api)


class TestGetData:

    def test_basic_schema(self):
        response = client.get("/data")
        data = response.json()

        assert response.status_code == 200

        assert "date" in data
        assert type(data["date"]) is str

        assert "energy_data" in data
        assert type(data["energy_data"]) is list

    def test_implicit_date(self):
        from datetime import date
        today_str = date.today().isoformat()

        response = client.get("/data/")
        data = response.json()

        assert response.status_code == 200

        assert data["date"] == today_str

    def test_explicit_date(self):
        today_str = "2020-06-04"

        response = client.get(f"/data/{today_str}")
        data = response.json()

        assert response.status_code == 200

        assert data["date"] == today_str

    @pytest.mark.projectwise
    def test_sensors(self):
        sensors = "timestamp,power,external_temp"

        response = client.get(f"/data/2022-05-10?sensors={sensors}")
        data = response.json()

        for sensor in sensors.split(","):
            assert sensor in data["energy_data"][0]

    def test_bad_date(self):
        today_str = "2020-06-34"

        response = client.get(f"/data/{today_str}")
        data = response.json()

        assert response.status_code == 400

        assert "message" in data
        assert today_str in data["message"]

    def test_bad_date_range_1(self):
        """The to_date is an invalid date"""

        to_date = "2000"

        response = client.get(f"/data?to_date={to_date}")
        data = response.json()

        assert response.status_code == 400

        assert "message" in data
        assert to_date in data["message"]

    def test_bad_date_range_2(self):
        """The first date is valid and corresponds to "today". The second date is valid, but in bad order."""
        to_date = "2000-01-01"

        response = client.get(f"/data?to_date={to_date}")
        data = response.json()

        assert response.status_code == 400

        assert "message" in data
        assert to_date in data["message"]
