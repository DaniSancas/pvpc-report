from pvpc.port import InputPort, OutputPort

import json

import requests


class PrecioLuzInputAdapter(InputPort):

    endpoint: str = "https://api.preciodelaluz.org/v1/prices/all?zone=PCB"

    def get_raw_data(self) -> dict:
        response = requests.get(self.endpoint)
        response.raise_for_status()

        return json.loads(response.text)


class TelegramOutputAdapter(OutputPort):
    def post_processed_data(data: dict):
        pass
