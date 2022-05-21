import pytest
from moosir_feature.news_feature.app_settings import Settings
from moosir_feature.news_feature.news_manager import *
import os

TEMP_FILE = "temp.h5"


@pytest.fixture()
def set_up():
    # set up
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)

    yield "set_up"

    # tear down
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)


def test_get_news_month(set_up):
    # arrange
    settings = Settings()

    dal = H5DataAccessLayer(file_path=TEMP_FILE, data_provider=settings.data_provider)
    manager = NewsFeatureManager(dal=dal, data_provider_tz=settings.data_provider_tz, countries=settings.countries)

    month = 1
    year = 2020

    # act
    manager.save_news_months(months=[1], year=2020)
    result = manager.get_news_month(month=month, year=year)
    # result = manager.get_news()

    # assert
    assert len(result[result["Timestamp"].dt.year != year]) == 0
    assert len(result[result["Timestamp"].dt.month != month]) == 0
    assert len(result[~result["currency"].isin(settings.countries)]) == 0
    assert len(result[result["importance"] != "high"]) == 0
    print(result)