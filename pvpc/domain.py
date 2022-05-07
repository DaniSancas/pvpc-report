from typing import List, Tuple
from pvpc.port import InputPort, OutputPort


class PVPCDay:

    number_of_2h_periods: int
    raw_data: dict
    am_prices: dict
    pm_prices: dict
    prices_of_2h_periods: dict
    sorted_prices_of_2h_periods: List[Tuple[str, float]]
    cheapest_6h: dict
    best_n_periods_of_2h: List[Tuple[str, float]]
    am_3h_periods: dict
    pm_3h_periods: dict
    sorted_am_3h_periods: List[Tuple[str, float]]
    sorted_pm_3h_periods: List[Tuple[str, float]]
    processed_data: dict

    def __init__(
        self,
        input_repo: InputPort,
        output_repo: OutputPort,
        number_of_2h_periods: int = 4,
    ) -> None:
        self.input_repo = input_repo
        self.output_repo = output_repo
        self.number_of_2h_periods = number_of_2h_periods

    def run(self):
        self.raw_data = self.input_repo.get_raw_data()

        self.cheapest_6h = self.get_6_cheapest_hours()
        self.prices_of_2h_periods = self.get_prices_of_2h_periods()
        self.sorted_prices_of_2h_periods = self.sort_prices_of_2h_periods()
        self.best_n_periods_of_2h = self.get_best_n_periods_of_2h()
        self.am_prices, self.pm_prices = self.split_am_and_pm()
        self.am_3h_periods = self.get_prices_for_3h_periods(is_am=True)
        self.pm_3h_periods = self.get_prices_for_3h_periods(is_am=False)
        self.sorted_am_3h_periods = self.sort_prices(is_am=True)
        self.sorted_pm_3h_periods = self.sort_prices(is_am=False)
        self.processed_data = self.collect_processed_data()

        self.output_repo.post_processed_data(self.processed_data)

    def collect_processed_data(self) -> dict:
        return {
            "cheapest_6h": self.cheapest_6h,
            "best_n_periods_of_2h": self.best_n_periods_of_2h,
        }
    
    def get_prices_for_3h_periods(self, is_am: bool) -> dict:
        prices = {}
        hour_range = range(10) if is_am else range(12, 22)

        for hour in hour_range:
            first_hour = self.get_hour_key_string_from_number(hour)
            second_hour = self.get_hour_key_string_from_number(hour + 1)
            third_hour = self.get_hour_key_string_from_number(hour + 2)
            first_hour_price = self.raw_data[first_hour]["price"]
            second_hour_price = self.raw_data[second_hour]["price"]
            third_hour_price = self.raw_data[third_hour]["price"]

            price_key = self.compose_key_from_2h(first_hour, third_hour)
            price_value = round(
                (first_hour_price + second_hour_price + third_hour_price) / 3, 2
            )
            prices[price_key] = price_value

        return prices

    def split_am_and_pm(self) -> Tuple[dict, dict]:
        am_dict = {}
        pm_dict = {}

        for k, v in self.raw_data.items():
            if int(k[:2]) < 12:
                am_dict.update({k: v})
            else:
                pm_dict.update({k: v})

        return am_dict, pm_dict

    def get_best_n_periods_of_2h(self) -> List[Tuple[str, float]]:
        return self.sorted_prices_of_2h_periods[0 : self.number_of_2h_periods]

    def dict_to_list_of_tuples(self, data: dict) -> List[Tuple[str, float]]:
        return [(k, v) for k, v in data.items()]

    def sort_prices(self, is_am: bool) -> List[Tuple[str, float]]:
        period_am_or_pm = self.am_3h_periods if is_am else self.pm_3h_periods

        prices = self.dict_to_list_of_tuples(period_am_or_pm)
        prices.sort(key=lambda price: price[1])

        return prices

    def sort_prices_of_2h_periods(self) -> List[Tuple[str, float]]:
        prices = self.dict_to_list_of_tuples(self.prices_of_2h_periods)
        prices.sort(key=lambda price: price[1])

        return prices

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
