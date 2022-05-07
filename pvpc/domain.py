from typing import List, Tuple
from pvpc.port import InputPort, OutputPort


class PVPCDay:

    raw_data: dict
    cheapest_6h: dict
    am_3h_periods: dict
    pm_3h_periods: dict
    sorted_am_3h_periods: List[Tuple[str, float]]
    sorted_pm_3h_periods: List[Tuple[str, float]]
    am_cheapest_3h_period: Tuple[str, float]
    pm_cheapest_3h_period: Tuple[str, float]
    am_cheapest_3h_period_unfolded: List[Tuple[str, float]]
    pm_cheapest_3h_period_unfolded: List[Tuple[str, float]]
    processed_data: dict

    def __init__(
        self,
        input_repo: InputPort,
        output_repo: OutputPort,
    ) -> None:
        self.input_repo = input_repo
        self.output_repo = output_repo

    def run(self):
        self.raw_data = self.input_repo.get_raw_data()

        self.cheapest_6h = self.get_6_cheapest_hours()

        self.am_3h_periods = self.get_prices_for_3h_periods(is_am=True)
        self.pm_3h_periods = self.get_prices_for_3h_periods(is_am=False)
        self.sorted_am_3h_periods = self.sort_prices(is_am=True)
        self.sorted_pm_3h_periods = self.sort_prices(is_am=False)
        self.am_cheapest_3h_period = self.get_best_period(is_am=True)
        self.pm_cheapest_3h_period = self.get_best_period(is_am=False)
        self.am_cheapest_3h_period_unfolded = self.get_best_period_unfolded(is_am=True)
        self.pm_cheapest_3h_period_unfolded = self.get_best_period_unfolded(is_am=False)

        self.processed_data = self.collect_processed_data()

        self.output_repo.post_processed_data(self.processed_data)

    def collect_processed_data(self) -> dict:
        return {
            "cheapest_6h": self.cheapest_6h,
            "am_cheapest_3h_period": self.am_cheapest_3h_period,
            "pm_cheapest_3h_period": self.pm_cheapest_3h_period,
            "am_cheapest_3h_period_unfolded": self.am_cheapest_3h_period_unfolded,
            "pm_cheapest_3h_period_unfolded": self.pm_cheapest_3h_period_unfolded,
        }

    def get_best_period_unfolded(self, is_am: bool) -> List[Tuple[str, float]]:
        prices = []
        sorted_period_am_or_pm = self.get_best_period(is_am=is_am)
        start_hour, stop_hour = self.decompose_key_from_2h(sorted_period_am_or_pm[0])

        for hour in range(int(start_hour), int(stop_hour)):
            formatted_hour = self.get_hour_key_string_from_number(hour)
            price = self.raw_data[formatted_hour]["price"]
            prices.append((formatted_hour, price))

        return prices

    def get_best_period(self, is_am: bool) -> Tuple[str, float]:
        sorted_period_am_or_pm = (
            self.sorted_am_3h_periods if is_am else self.sorted_pm_3h_periods
        )
        return sorted_period_am_or_pm[0]

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

    def dict_to_list_of_tuples(self, data: dict) -> List[Tuple[str, float]]:
        return [(k, v) for k, v in data.items()]

    def sort_prices(self, is_am: bool) -> List[Tuple[str, float]]:
        period_am_or_pm = self.am_3h_periods if is_am else self.pm_3h_periods

        prices = self.dict_to_list_of_tuples(period_am_or_pm)
        prices.sort(key=lambda price: price[1])

        return prices

    def get_6_cheapest_hours(self) -> dict:
        prices = {}
        for hour in range(24):
            formatted_hour = self.get_hour_key_string_from_number(hour)
            if self.raw_data[formatted_hour]["is-cheap"]:
                prices[formatted_hour] = self.raw_data[formatted_hour]["price"]
        return prices

    def compose_key_from_2h(self, first_hour: str, second_hour: str) -> str:
        return f"{first_hour[0:3]}{second_hour[3:5]}"

    def decompose_key_from_2h(self, composed_key: str) -> str:
        return composed_key[0:2], composed_key[3:5]

    def get_hour_key_string_from_number(self, hour: int) -> str:
        return f"{str(hour).zfill(2)}-{str(hour+1).zfill(2)}"
