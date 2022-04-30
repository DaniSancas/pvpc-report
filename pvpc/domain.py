from pvpc.port import InputPort, OutputPort


class PVPCDay:

    raw_data: dict
    clean_data: dict

    def __init__(self, input_repo: InputPort, output_repo: OutputPort) -> None:
        self.input_repo = input_repo
        self.output_repo = output_repo

    def run(self):
        self.raw_data = self.input_repo.get_raw_data()
        self.clean_data = self.clean_pvpc_data()
        self.prices_of_2h_periods = self.get_prices_of_2h_periods()

    def get_prices_of_2h_periods(self) -> dict:
        prices = {}

        for h in range(23):
            first_hour = self.get_hour_key_string_from_number(h)
            second_hour = self.get_hour_key_string_from_number(h + 1)
            first_hour_price = self.raw_data[first_hour]["price"]
            second_hour_price = self.raw_data[second_hour]["price"]

            price_key = self.compose_key_from_2h(first_hour, second_hour)
            price_value = round((first_hour_price + second_hour_price) / 2, 2)
            prices[price_key] = price_value

        return prices

    def compose_key_from_2h(self, first_hour: str, second_hour: str) -> str:
        return f"{first_hour[0:3]}{second_hour[3:5]}"

    def get_hour_key_string_from_number(self, hour: int) -> str:
        return f"{str(hour).zfill(2)}-{str(hour+1).zfill(2)}"

    def clean_hourly_data(self, hour_data: dict) -> dict:
        cleaned_data = hour_data.copy()
        cleaned_data["hour"] = cleaned_data["hour"][0:2]
        return cleaned_data

    def clean_pvpc_data(self) -> dict:
        cleaned_data = {}

        for hour_key, hour_value in self.raw_data.items():
            cleaned_hour_key = hour_key[0:2]
            cleaned_hour_value = self.clean_hourly_data(hour_value)

            cleaned_data[cleaned_hour_key] = cleaned_hour_value

        return cleaned_data
