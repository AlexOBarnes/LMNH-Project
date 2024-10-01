'''Extraction of the data'''
import logging
import requests
import asyncio
import pandas as pd

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://data-eng-plants-api.herokuapp.com"


def get_url(id: int):
    '''Gets the API url'''
    url = f"{BASE_URL}/plants/{id}"
    return url


def get_num_plants() -> int:
    '''Return the number of plants on display.'''

    response = requests.get(BASE_URL, timeout=10)

    if response.status_code != 200:
        raise ValueError("Request unsuccessful.")

    if response.json().get("success", False):
        return int(response["plants_on_display"])

    return 0


def extract() -> pd.DataFrame:
    '''Return a dataframe with the extracted data'''


if __name__ == "__main__":
    ...
