'''Extraction of the data'''
import logging

import requests

import asyncio
import pandas as pd

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://data-eng-plants-api.herokuapp.com"

REQUIRED_FIELDS = ["botanist", "plant_id"]


def get_url(id: int):
    '''Gets the API url'''

    url = f"{BASE_URL}/plants/{id}"
    return url


def get_num_plants() -> int:
    '''Return the number of plants on display.'''

    response = requests.get(BASE_URL, timeout=10)

    if response.status_code != 200:
        logging.error("Invalid response %s", response.status_code)
        raise ValueError("Request unsuccessful.")

    num_plants = response.json().get("success", False)
    if num_plants is not False:
        logging.info("Number of plants on display is %s", num_plants)
        return int(num_plants)

    return 0


def validate_reponse(response: dict) -> bool:
    '''Return True if a response is valid'''
    if not all(response.get(k, False) for k in REQUIRED_FIELDS):
        logging.warning("response %s is missing required fields", response)
        return False
    return True


def extract() -> pd.DataFrame:
    '''Return a dataframe with the extracted data'''


if __name__ == "__main__":
    ...
