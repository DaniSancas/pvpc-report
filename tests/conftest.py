import json
import sys, os

import pytest


# Make sure that the application source directory (this directory's parent) is
# on sys.path.

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, here)


DAILY_SAMPLE_PATH = "tests/fixtures/daily_sample.json"
PRICES_2H_PERIODS = "tests/fixtures/2h_periods.json"


@pytest.fixture
def raw_data() -> dict:
    with open(DAILY_SAMPLE_PATH, "r") as daily_sample:
        data = json.load(daily_sample)
    return data


@pytest.fixture
def prices_2h_periods_data() -> dict:
    with open(PRICES_2H_PERIODS, "r") as prices_2h:
        data = json.load(prices_2h)
    return data
