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

    def list_of_tuples_to_str(self, data: List[Tuple[str, float]]) -> str:
        return "".join([f"{k}: {str(v)} €/Mwh\n" for k, v in data])

    def dict_to_str(self, data: dict) -> str:
        return "".join([f"{k}: {str(v)} €/Mwh\n" for k, v in data.items()])

    def generate_message(self, data: dict) -> str:
        message = "Precios de la luz para hoy\n"
        message += "\n*Las horas más baratas:*\n"
        message += self.dict_to_str(data["cheapest_6h"])
        message += "\n*Los rangos de 2h más baratos*\n"
        message += "_(precio medio de ambas horas)_:\n"
        message += self.list_of_tuples_to_str(data["best_n_periods_of_2h"])
        return message

    def post_processed_data(self, data: dict):
        message = self.generate_message(data)

        status = self.bot.send_message(
            chat_id=self.channel, text=message, parse_mode=telegram.ParseMode.MARKDOWN
        )
        print(status)
