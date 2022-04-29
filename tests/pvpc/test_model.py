import json

import pytest
import requests_mock
from deepdiff import DeepDiff
from requests.exceptions import HTTPError

from pvpc.model import PVPCDay


class TestModel:

    DAILY_SAMPLE_PATH = 'tests/fixtures/daily_sample.json'

    @pytest.fixture
    def raw_data(self) -> dict:
        with open(self.DAILY_SAMPLE_PATH, "r") as daily_sample:
            data = json.load(daily_sample)
        return data

    @pytest.fixture
    def model_with_raw(self, raw_data: dict) -> PVPCDay:
        pvpc_day = PVPCDay()
        pvpc_day.raw_data = raw_data

        return pvpc_day

    def test_get_today_raw_pvpc_data_success(self, raw_data: dict):
        with requests_mock.Mocker() as mock:
            mock.get(f"{PVPCDay.endpoint}", json=raw_data)
            data = PVPCDay().get_today_raw_pvpc_data()
        
        assert len(data) == 24
        assert "price" in data["00-01"]
        assert data["00-01"]["price"] == 254.96

    def test_get_today_raw_pvpc_data_error(self):
        with requests_mock.Mocker() as mock:
            with pytest.raises(HTTPError):
                mock.get(PVPCDay.endpoint, text='Not Found', status_code=404)
                _ = PVPCDay().get_today_raw_pvpc_data()

    def test_clean_hourly_data(self, model_with_raw: PVPCDay):
        hour_to_test = model_with_raw.raw_data["00-01"]

        expected_output = {
            "date": "29-04-2022",
            "hour": "00",
            "is-cheap": True,
            "is-under-avg": True,
            "market": "PVPC",
            "price": 254.96,
            "units": "€/Mwh"
        }

        output = model_with_raw.clean_hourly_data(hour_data=hour_to_test)

        assert expected_output['hour'] == output['hour']
        assert DeepDiff(expected_output, output) == {}

    def test_clean_pvpc_data(self, model_with_raw: PVPCDay):
        data_to_clean = model_with_raw.raw_data
        expected_keys = [str(h).zfill(2) for h in range(24)]

        output = model_with_raw.clean_pvpc_data(raw_data=data_to_clean)

        assert set(expected_keys) == set(output.keys())

    def test_run(self, raw_data: dict):
        with requests_mock.Mocker() as mock:
            mock.get(f"{PVPCDay.endpoint}", json=raw_data)
            pvpc = PVPCDay()
            pvpc.run()
        
        assert len(pvpc.raw_data) == 24
        assert "price" in pvpc.raw_data["00-01"]
        assert pvpc.raw_data["00-01"]["price"] == 254.96
        assert pvpc.raw_data["00-01"]["hour"] == "00-01"

        assert len(pvpc.clean_data) == 24
        assert "price" in pvpc.clean_data["00"]
        assert pvpc.clean_data["00"]["price"] == 254.96
        assert pvpc.clean_data["00"]["hour"] == "00"
