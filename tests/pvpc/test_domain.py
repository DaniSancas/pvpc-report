from typing import Tuple
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

    @pytest.mark.parametrize(
        "composed_key, expected_first_hour, expected_second_hour",
        [
            ("02-03", "02", "03"),
            ("00-02", "00", "02"),
            ("01-04", "01", "04"),
        ],
        ids=["1h", "2h", "3h"],
    )
    def test_decompose_key_from_2h(
        self,
        composed_key: str,
        expected_first_hour: str,
        expected_second_hour: str,
        domain_with_raw: PVPCDay,
    ):
        assert (
            expected_first_hour,
            expected_second_hour,
        ) == domain_with_raw.decompose_key_from_2h(composed_key)

    def test_dict_to_list_of_tuples(self, domain_with_raw: PVPCDay):
        input = {
            "key": "value",
            "something": "else",
        }

        expected = [("key", "value"), ("something", "else")]

        output = domain_with_raw.dict_to_list_of_tuples(input)

        assert set(expected) == set(output)

    def test_collect_processed_data(self, domain_with_raw: PVPCDay):
        input_cheapest_6h = {
            "00-01": 254.96,
            "01-02": 255.29,
            "02-03": 256.76,
            "03-04": 258.82,
            "14-15": 253.06,
            "15-16": 256.81,
        }

        input_am_cheapest_3h_period = ("00-03", 255.67)
        input_pm_cheapest_3h_period = ("14-17", 259.52)

        input_am_cheapest_3h_period_unfolded = [
            ("00-01", 254.96),
            ("01-02", 255.29),
            ("02-03", 256.76),
        ]
        input_pm_cheapest_3h_period_unfolded = [
            ("14-15", 253.06),
            ("15-16", 256.81),
            ("16-17", 268.7),
        ]

        expected = {
            "cheapest_6h": input_cheapest_6h,
            "am_cheapest_3h_period": input_am_cheapest_3h_period,
            "pm_cheapest_3h_period": input_pm_cheapest_3h_period,
            "am_cheapest_3h_period_unfolded": input_am_cheapest_3h_period_unfolded,
            "pm_cheapest_3h_period_unfolded": input_pm_cheapest_3h_period_unfolded,
        }

        domain_with_raw.cheapest_6h = input_cheapest_6h
        domain_with_raw.am_cheapest_3h_period = input_am_cheapest_3h_period
        domain_with_raw.pm_cheapest_3h_period = input_pm_cheapest_3h_period
        domain_with_raw.am_cheapest_3h_period_unfolded = (
            input_am_cheapest_3h_period_unfolded
        )
        domain_with_raw.pm_cheapest_3h_period_unfolded = (
            input_pm_cheapest_3h_period_unfolded
        )

        output = domain_with_raw.collect_processed_data()

        assert DeepDiff(expected, output) == {}

    @pytest.mark.parametrize(
        "is_am",
        [True, False],
        ids=["am", "pm"],
    )
    def test_get_prices_for_3h_periods(
        self,
        is_am: bool,
        domain_with_raw: PVPCDay,
        am_prices_3h_periods_data: dict,
        pm_prices_3h_periods_data: dict,
    ):
        expected = am_prices_3h_periods_data if is_am else pm_prices_3h_periods_data
        output = domain_with_raw.get_prices_for_3h_periods(is_am=is_am)

        assert DeepDiff(expected, output) == {}

    @pytest.mark.parametrize(
        "is_am, input_data, expected",
        [
            (
                True,
                {
                    "00-03": 260.1,
                    "01-04": 250.2,
                    "02-05": 240.3,
                    "03-06": 270.4,
                },
                [
                    ("02-05", 240.3),
                    ("01-04", 250.2),
                    ("00-03", 260.1),
                    ("03-06", 270.4),
                ],
            ),
            (
                False,
                {
                    "12-15": 260.1,
                    "13-16": 250.2,
                    "14-17": 240.3,
                    "15-18": 270.4,
                },
                [
                    ("14-17", 240.3),
                    ("13-16", 250.2),
                    ("12-15", 260.1),
                    ("15-18", 270.4),
                ],
            ),
        ],
        ids=["am", "pm"],
    )
    def test_sort_prices(
        self, is_am: bool, input_data: dict, expected: list, domain_with_dummy: PVPCDay
    ):
        if is_am:
            domain_with_dummy.am_3h_periods = input_data
        else:
            domain_with_dummy.pm_3h_periods = input_data

        output = domain_with_dummy.sort_prices(is_am=is_am)

        assert set(expected) == set(output)

    @pytest.mark.parametrize(
        "is_am, input_data, expected",
        [
            (
                True,
                [
                    ("02-05", 240.3),
                    ("01-04", 250.2),
                    ("00-03", 260.1),
                    ("03-06", 270.4),
                ],
                ("02-05", 240.3),
            ),
            (
                False,
                [
                    ("14-17", 240.3),
                    ("13-16", 250.2),
                    ("12-15", 260.1),
                    ("15-18", 270.4),
                ],
                ("14-17", 240.3),
            ),
        ],
        ids=["am", "pm"],
    )
    def test_get_best_period(
        self,
        is_am: bool,
        input_data: list,
        expected: Tuple[str, float],
        domain_with_dummy: PVPCDay,
    ):
        pvpc = domain_with_dummy
        if is_am:
            pvpc.sorted_am_3h_periods = input_data
        else:
            pvpc.sorted_pm_3h_periods = input_data

        output = pvpc.get_best_period(is_am=is_am)

        assert set(expected) == set(output)

    @pytest.mark.parametrize(
        "is_am, input_data, expected",
        [
            (
                True,
                [
                    ("00-03", 255.67),
                    ("01-04", 256.96),
                    ("02-05", 258.97),
                    ("03-06", 263.57),
                ],
                [
                    ("00-01", 254.96),
                    ("01-02", 255.29),
                    ("02-03", 256.76),
                ],
            ),
            (
                False,
                [
                    ("14-17", 259.52),
                    ("13-16", 271.0),
                    ("12-15", 288.16),
                    ("15-18", 267.81),
                ],
                [
                    ("14-15", 253.06),
                    ("15-16", 256.81),
                    ("16-17", 268.7),
                ],
            ),
        ],
        ids=["am", "pm"],
    )
    def test_get_best_period_unfolded(
        self,
        is_am: bool,
        input_data: list,
        expected: list,
        domain_with_raw: PVPCDay,
    ):
        pvpc = domain_with_raw
        if is_am:
            pvpc.sorted_am_3h_periods = input_data
        else:
            pvpc.sorted_pm_3h_periods = input_data

        output = pvpc.get_best_period_unfolded(is_am=is_am)

        assert set(expected) == set(output)

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
        processed_data_keys = {
            "cheapest_6h",
            "am_cheapest_3h_period",
            "pm_cheapest_3h_period",
            "am_cheapest_3h_period_unfolded",
            "pm_cheapest_3h_period_unfolded",
        }

        pvpc.run()

        assert len(pvpc.raw_data) == 24
        assert "price" in pvpc.raw_data["00-01"]
        assert pvpc.raw_data["00-01"]["price"] == 254.96
        assert pvpc.raw_data["00-01"]["hour"] == "00-01"

        assert len(pvpc.cheapest_6h) == 6
        assert pvpc.cheapest_6h["00-01"] == 254.96
        assert pvpc.cheapest_6h["15-16"] == 256.81

        assert pvpc.am_cheapest_3h_period == ("00-03", 255.67)
        assert pvpc.pm_cheapest_3h_period == ("14-17", 259.52)

        assert pvpc.am_cheapest_3h_period_unfolded == [
            ("00-01", 254.96),
            ("01-02", 255.29),
            ("02-03", 256.76),
        ]
        assert pvpc.pm_cheapest_3h_period_unfolded == [
            ("14-15", 253.06),
            ("15-16", 256.81),
            ("16-17", 268.7),
        ]

        assert len(pvpc.processed_data) == 5
        assert processed_data_keys == pvpc.processed_data.keys()
        assert pvpc.processed_data["cheapest_6h"]["00-01"] == 254.96
        assert pvpc.processed_data["cheapest_6h"]["15-16"] == 256.81
