from typing import List, Tuple
from pvpc.port import InputPort, OutputPort

import json

import telegram
import requests


class PrecioLuzInputAdapter(InputPort):

    endpoint: str = "https://api.preciodelaluz.org/v1/prices/all?zone=PCB"

    def get_raw_data(self) -> dict:
        response = requests.get(self.endpoint)
        response.raise_for_status()

        return json.loads(response.text)


class TelegramOutputAdapter(OutputPort):

    bot: telegram.Bot
    channel: str

    def __init__(self, token: str, channel: str) -> None:
        self.channel = channel
        self.bot = telegram.Bot(token=token)

    def tuple_to_str(self, tuple: Tuple[str, float]) -> str:
        return self.key_value_pair_to_str(tuple[0], tuple[1])

    def key_value_pair_to_str(self, k: str, v: float) -> str:
        return f"{k}: {str(v)} €/mWh\n"

    def list_of_tuples_to_str(self, data: List[Tuple[str, float]]) -> str:
        return "".join([self.key_value_pair_to_str(k, v) for k, v in data])

    def dict_to_str(self, data: dict) -> str:
        return "".join([self.key_value_pair_to_str(k, v) for k, v in data.items()])

    def generate_message(self, data: dict) -> str:
        message = "Precios de la luz para hoy:\n"

        message += "\n*Las horas más baratas:*\n"
        message += self.dict_to_str(data["cheapest_6h"])

        message += "\n\n*Periodos AM/PM más baratos:*\n"

        message += "\n*AM* -> Periodo (3h) más barato:\n"
        message += self.tuple_to_str(data["am_cheapest_3h_period"])
        message += "\nDetalle por hora:\n"
        message += self.list_of_tuples_to_str(data["am_cheapest_3h_period_unfolded"])

        message += "\n*PM* -> Periodo (3h) más barato:\n"
        message += self.tuple_to_str(data["pm_cheapest_3h_period"])
        message += "\nDetalle por hora:\n"
        message += self.list_of_tuples_to_str(data["pm_cheapest_3h_period_unfolded"])

        return message

    def post_processed_data(self, data: dict):
        message = self.generate_message(data)

        status = self.bot.send_message(
            chat_id=self.channel, text=message, parse_mode=telegram.ParseMode.MARKDOWN
        )
        print(status)
