import json
import pytest
from requests.exceptions import (HTTPError)
import requests_mock

from pvpc.model import PVPCDay

class TestModel:

    DAILY_SAMPLE_PATH = 'tests/fixtures/daily_sample.json'

    def test_get_today_raw_pvpc_data_success(self):
        with open(self.DAILY_SAMPLE_PATH, "r") as daily_sample:
            with requests_mock.Mocker() as mock:
                mock.get(f"{PVPCDay.endpoint}", json=json.load(daily_sample))
                data = PVPCDay().get_today_raw_pvpc_data()
        
        assert len(data) == 24
        assert "price" in data["00-01"]
        assert data["00-01"]["price"] == 254.96

    def test_get_today_raw_pvpc_data_error(self):
        with requests_mock.Mocker() as mock:
            with pytest.raises(HTTPError):
                mock.get(PVPCDay.endpoint, text='Not Found', status_code=404)
                data = PVPCDay().get_today_raw_pvpc_data()
