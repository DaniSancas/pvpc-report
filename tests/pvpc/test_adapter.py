import pytest
from requests import HTTPError
import requests_mock

from pvpc.adapter import PrecioLuzInputAdapter, TelegramOutputAdapter, telegram


@pytest.fixture()
def bot_with_dummy(monkeypatch) -> TelegramOutputAdapter:
    def mock_bot(token: str):
        return None

    monkeypatch.setattr(telegram, "Bot", mock_bot)
    return TelegramOutputAdapter(None, None)


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

    def test_tuple_to_str(self, bot_with_dummy: TelegramOutputAdapter):
        input_data = ("00-01", 254.96)

        expected = "00-01: 254.96 €/mWh\n"
        output = bot_with_dummy.tuple_to_str(input_data)

        assert expected == output

    def test_key_value_pair_to_str(self, bot_with_dummy: TelegramOutputAdapter):
        input_key, input_value = ("00-01", 254.96)

        expected = "00-01: 254.96 €/mWh\n"
        output = bot_with_dummy.key_value_pair_to_str(input_key, input_value)

        assert expected == output

    def test_list_of_tuples_to_str(self, bot_with_dummy: TelegramOutputAdapter):
        input = {
            "00-01": 254.96,
            "01-02": 255.29,
            "02-03": 256.76,
            "03-04": 258.82,
            "14-15": 253.06,
            "15-16": 256.81,
        }

        expected = (
            "00-01: 254.96 €/mWh\n"
            "01-02: 255.29 €/mWh\n"
            "02-03: 256.76 €/mWh\n"
            "03-04: 258.82 €/mWh\n"
            "14-15: 253.06 €/mWh\n"
            "15-16: 256.81 €/mWh\n"
        )
        output = bot_with_dummy.dict_to_str(input)

        assert expected == output

    def test_list_of_tuples_to_str(self, bot_with_dummy: TelegramOutputAdapter):
        input = [
            ("22-23", 240),
            ("01-02", 250),
            ("00-01", 260),
            ("23-24", 270),
        ]

        expected = (
            "22-23: 240 €/mWh\n"
            "01-02: 250 €/mWh\n"
            "00-01: 260 €/mWh\n"
            "23-24: 270 €/mWh\n"
        )

        output = bot_with_dummy.list_of_tuples_to_str(input)

        assert expected == output
