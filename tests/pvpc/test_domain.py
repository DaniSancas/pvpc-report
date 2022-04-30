import pytest
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
        expected_keys = [str(h).zfill(2) for h in range(24)]

        output = domain_with_raw.clean_pvpc_data()

        assert set(expected_keys) == set(output.keys())

    @pytest.mark.parametrize(
        "hour, expected",
        [
            (0, "00-01"),
            (1, "01-02"),
            (22, "22-23"),
            (23, "23-24"),
        ],
        ids=["0", "1", "22", "23"],
    )
    def test_get_hour_key_string_from_number(
        self, hour: int, expected: str, domain_with_dummy: PVPCDay
    ):
        assert expected == domain_with_dummy.get_hour_key_string_from_number(hour)

    @pytest.mark.parametrize(
        "first_hour, second_hour, expected",
        [
            ("00-01", "01-02", "00-02"),
            ("01-02", "02-03", "01-03"),
            ("21-22", "22-23", "21-23"),
            ("22-23", "23-24", "22-24"),
        ],
        ids=["00-02", "01-03", "21-23", "22-24"],
    )
    def test_compose_key_from_2h(
        self, first_hour, second_hour, expected, domain_with_dummy: PVPCDay
    ):
        assert expected == domain_with_dummy.compose_key_from_2h(
            first_hour, second_hour
        )

    def test_get_prices_of_2h_periods(
        self, domain_with_raw: PVPCDay, prices_2h_periods_data: dict
    ):
        expected = prices_2h_periods_data
        output = domain_with_raw.get_prices_of_2h_periods()

        assert DeepDiff(expected, output) == {}

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
