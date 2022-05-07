import json
import sys, os

import pytest


# Make sure that the application source directory (this directory's parent) is
# on sys.path.

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, here)


DAILY_SAMPLE_PATH = "tests/fixtures/daily_sample.json"
AM_PRICES_3H_PERIODS = "tests/fixtures/am_3h_periods.json"
PM_PRICES_3H_PERIODS = "tests/fixtures/pm_3h_periods.json"


@pytest.fixture
def raw_data() -> dict:
    with open(DAILY_SAMPLE_PATH, "r") as daily_sample:
        data = json.load(daily_sample)
    return data


@pytest.fixture
def am_prices_3h_periods_data() -> dict:
    with open(AM_PRICES_3H_PERIODS, "r") as am_prices_3h:
        data = json.load(am_prices_3h)
    return data


@pytest.fixture
def pm_prices_3h_periods_data() -> dict:
    with open(PM_PRICES_3H_PERIODS, "r") as pm_prices_3h:
        data = json.load(pm_prices_3h)
    return data
