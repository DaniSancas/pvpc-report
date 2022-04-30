from pvpc.port import InputPort, OutputPort


class PVPCDay:

    raw_data: dict
    clean_data: dict

    def __init__(self, input_repo: InputPort, output_repo: OutputPort) -> None:
        self.input_repo = input_repo
        self.output_repo = output_repo

    def run(self):
        self.raw_data = self.input_repo.get_raw_data()
        self.clean_data = self.clean_pvpc_data(self.raw_data)

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
