from pvpc.port import InputPort, OutputPort


class PVPCDay:

    raw_data: dict
    prices_of_2h_periods: dict
    cheapest_6h: dict
    best_n_prices: dict
    worst_n_prices: dict

    def __init__(
        self,
        input_repo: InputPort,
        output_repo: OutputPort,
    ) -> None:
        self.input_repo = input_repo
        self.output_repo = output_repo

    def run(self):
        self.raw_data = self.input_repo.get_raw_data()
        self.prices_of_2h_periods = self.get_prices_of_2h_periods()
        self.cheapest_6h = self.get_6_cheapest_hours()

    def get_6_cheapest_hours(self) -> dict:
        prices = {}
        for hour in range(24):
            formatted_hour = self.get_hour_key_string_from_number(hour)
            if self.raw_data[formatted_hour]["is-cheap"]:
                prices[formatted_hour] = self.raw_data[formatted_hour]["price"]
        return prices

    def get_prices_of_2h_periods(self) -> dict:
        prices = {}

        for hour in range(23):
            first_hour = self.get_hour_key_string_from_number(hour)
            second_hour = self.get_hour_key_string_from_number(hour + 1)
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
