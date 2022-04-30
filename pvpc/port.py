from abc import ABC, abstractmethod


class InputPort(ABC):
    @abstractmethod
    def get_raw_data() -> dict:
        pass


class OutputPort(ABC):
    @abstractmethod
    def post_processed_data(data: dict):
        pass
