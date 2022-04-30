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
        self, first_hour, second_hour, expected, domain_with_raw: PVPCDay
    ):
        assert expected == domain_with_raw.compose_key_from_2h(first_hour, second_hour)

    def test_dict_to_list_of_tuples(self, domain_with_raw: PVPCDay):
        input = {
            "key": "value",
            "something": "else",
        }

        expected = [("key", "value"), ("something", "else")]

        output = domain_with_raw.dict_to_list_of_tuples(input)

        assert set(expected) == set(output)

    def test_get_best_n_periods_of_2h(self, domain_with_raw: PVPCDay):
        input = [
            ("22-23", 240),
            ("01-02", 250),
            ("00-01", 260),
            ("23-24", 270),
        ]

        expected = [
            ("22-23", 240),
            ("01-02", 250),
        ]

        domain_with_raw.number_of_2h_periods = 2
        domain_with_raw.sorted_prices_of_2h_periods = input
        output = domain_with_raw.get_best_n_periods_of_2h()

        assert set(expected) == set(output)

    def test_sort_prices_of_2h_periods(self, domain_with_raw: PVPCDay):
        input = {
            "00-01": 260,
            "01-02": 250,
            "22-23": 240,
            "23-24": 270,
        }

        expected = [
            ("22-23", 240),
            ("01-02", 250),
            ("00-01", 260),
            ("23-24", 270),
        ]

        domain_with_raw.prices_of_2h_periods = input

        output = domain_with_raw.sort_prices_of_2h_periods()

        assert set(expected) == set(output)

    def test_get_prices_of_2h_periods(
        self, domain_with_raw: PVPCDay, prices_2h_periods_data: dict
    ):
        expected = prices_2h_periods_data
        output = domain_with_raw.get_prices_of_2h_periods()

        assert DeepDiff(expected, output) == {}

    def test_get_6_cheapest_hours(self, domain_with_raw: PVPCDay):
        expected = {
            "00-01": 254.96,
            "01-02": 255.29,
            "02-03": 256.76,
            "03-04": 258.82,
            "14-15": 253.06,
            "15-16": 256.81,
        }

        output = domain_with_raw.get_6_cheapest_hours()

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

        assert len(pvpc.cheapest_6h) == 6
        assert pvpc.cheapest_6h["00-01"] == 254.96
        assert pvpc.cheapest_6h["15-16"] == 256.81

        assert len(pvpc.prices_of_2h_periods) == 23
        assert pvpc.prices_of_2h_periods["00-02"] == 255.12
        assert pvpc.prices_of_2h_periods["22-24"] == 310.88

        assert len(pvpc.sorted_prices_of_2h_periods) == 23
        assert pvpc.sorted_prices_of_2h_periods[0][0] == "14-16"
        assert pvpc.sorted_prices_of_2h_periods[0][1] == 254.94
        assert pvpc.sorted_prices_of_2h_periods[-1][0] == "20-22"
        assert pvpc.sorted_prices_of_2h_periods[-1][1] == 381.50

        assert len(pvpc.best_n_periods_of_2h) == pvpc.number_of_2h_periods
        assert pvpc.best_n_periods_of_2h[0][0] == "14-16"
        assert pvpc.best_n_periods_of_2h[0][1] == 254.94
