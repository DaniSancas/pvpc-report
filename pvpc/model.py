import requests
import json

class PVPCDay:

    endpoint = 'https://api.preciodelaluz.org/v1/prices/all?zone=PCB'

    def get_today_raw_pvpc_data(self) -> dict:
        response = requests.get(self.endpoint)
        response.raise_for_status()

        return json.loads(response.text)
