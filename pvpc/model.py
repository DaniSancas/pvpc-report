import json

import requests


class PVPCDay:

    endpoint = "https://api.preciodelaluz.org/v1/prices/all?zone=PCB"
    raw_data: dict
    clean_data: dict

    def run(self):
        self.raw_data = self.get_today_raw_pvpc_data()
        self.clean_data = self.clean_pvpc_data(self.raw_data)

    def get_today_raw_pvpc_data(self) -> dict:
        response = requests.get(self.endpoint)
        response.raise_for_status()

        return json.loads(response.text)

    def clean_hourly_data(self, hour_data: dict) -> dict:
        cleaned_data = hour_data.copy()
        cleaned_data["hour"] = cleaned_data["hour"][0:2]
        return cleaned_data

    def clean_pvpc_data(self, raw_data: dict) -> dict:
        cleaned_data = {}

        for hour_key, hour_value in raw_data.items():
            cleaned_hour_key = hour_key[0:2]
            cleaned_hour_value = self.clean_hourly_data(hour_value)

            cleaned_data[cleaned_hour_key] = cleaned_hour_value

        return cleaned_data
