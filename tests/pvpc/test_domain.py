import pytest
import requests_mock
from deepdiff import DeepDiff
from pvpc.domain import PVPCDay
from pvpc.port import InputPort, OutputPort


class DummyInputAdapter(InputPort):
    def get_raw_data(self) -> dict:
        pass


class DummyOutputAdapter(OutputPort):
    def post_processed_data(self, data: dict):
        pass


class TestDomain:
    @pytest.fixture()
    def domain_with_dummy(self) -> PVPCDay:
        input_repo = DummyInputAdapter()
        output_repo = DummyOutputAdapter()
        return PVPCDay(input_repo, output_repo)

    @pytest.fixture()
    def domain_with_raw(self, domain_with_dummy: PVPCDay, raw_data: dict) -> PVPCDay:
        domain_with_dummy.raw_data = raw_data
        return domain_with_dummy

    def test_clean_hourly_data(self, domain_with_raw: PVPCDay):
        hour_to_test = domain_with_raw.raw_data["00-01"]

        expected_output = {
            "date": "29-04-2022",
            "hour": "00",
            "is-cheap": True,
            "is-under-avg": True,
            "market": "PVPC",
            "price": 254.96,
            "units": "€/Mwh",
        }

        output = domain_with_raw.clean_hourly_data(hour_data=hour_to_test)

        assert expected_output["hour"] == output["hour"]
        assert DeepDiff(expected_output, output) == {}

    def test_clean_pvpc_data(self, domain_with_raw: PVPCDay):
        data_to_clean = domain_with_raw.raw_data
        expected_keys = [str(h).zfill(2) for h in range(24)]

        output = domain_with_raw.clean_pvpc_data(raw_data=data_to_clean)

        assert set(expected_keys) == set(output.keys())

    def test_run(self, monkeypatch, domain_with_dummy: PVPCDay, raw_data: dict):
        def mock_raw_data():
            return raw_data

        pvpc = domain_with_dummy
        monkeypatch.setattr(pvpc.input_repo, "get_raw_data", mock_raw_data)

        pvpc.run()

        assert len(pvpc.raw_data) == 24
        assert "price" in pvpc.raw_data["00-01"]
        assert pvpc.raw_data["00-01"]["price"] == 254.96
        assert pvpc.raw_data["00-01"]["hour"] == "00-01"

        assert len(pvpc.clean_data) == 24
        assert "price" in pvpc.clean_data["00"]
        assert pvpc.clean_data["00"]["price"] == 254.96
        assert pvpc.clean_data["00"]["hour"] == "00"
