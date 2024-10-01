'''Extraction of the data'''
import logging

import requests

import asyncio
import aiohttp
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


def get_plant_data(plant_id: int) -> dict | None:
    '''Return data from a plant_id endpoint'''

    response = requests.get(get_url(plant_id), timeout=10)
    if response.status_code == 200:
        LOGGER.info("Retrieved data for plant %s", plant_id)
        data = response.json()
        if validate_reponse(data):
            return data

    LOGGER.warning("Unseccessful response for plant %s", plant_id)
    return None


async def get_plant_data(session: aiohttp.ClientSession, plant_id: int) -> dict | None:
    '''Return data from a plant_id endpoint asynchronously'''
    async with session.get(get_url(plant_id)) as response:
        if response.status == 200:
            LOGGER.info("Retrieved data for plant %s", plant_id)
            data = await response.json()
            if validate_response(data):
                return data

        LOGGER.warning("Unsuccessful response for plant %s", plant_id)
        return None


def extract() -> pd.DataFrame:
    '''Return a dataframe with the extracted data'''
    num_plants = get_num_plants()


if __name__ == "__main__":
    ...
