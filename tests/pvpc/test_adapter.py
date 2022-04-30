import pytest
from requests import HTTPError
import requests_mock

from pvpc.adapter import PrecioLuzInputAdapter


class TestAdapter:
    def test_get_raw_data_success(self, raw_data: dict):
        with requests_mock.Mocker() as mock:
            mock.get(f"{PrecioLuzInputAdapter.endpoint}", json=raw_data)
            input_repo = PrecioLuzInputAdapter()
            data = input_repo.get_raw_data()

        assert len(data) == 24
        assert "price" in data["00-01"]
        assert data["00-01"]["price"] == 254.96

    def test_get_raw_data_error(self):
        with requests_mock.Mocker() as mock:
            with pytest.raises(HTTPError):
                mock.get(
                    PrecioLuzInputAdapter.endpoint, text="Not Found", status_code=404
                )
                input_repo = PrecioLuzInputAdapter()
                _ = input_repo.get_raw_data()
