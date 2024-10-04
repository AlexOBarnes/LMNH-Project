'''Extraction of the data'''
import logging

from time import perf_counter

import requests
import asyncio
import aiohttp

from logger import logger_setup

LOGGER = logging.getLogger(__name__)

BASE_URL = "http://data-eng-plants-api.herokuapp.com/"

REQUIRED_FIELDS = ["botanist", "plant_id"]


def get_url(id: int) -> str:
    '''Gets the API url'''

    url = f"{BASE_URL}/plants/{id}"
    return url


def get_num_plants() -> int:
    '''Return the number of plants on display.'''
    timer = perf_counter()
    response = requests.get(BASE_URL, timeout=10).json()

    if response.get("success", False) is not False:
        num_plants = response.get("plants_on_display")
        LOGGER.info("Number of plants on display is %s", num_plants)

        LOGGER.info("Time taken to retrieve plant count: %s",
                    str(round(perf_counter()-timer, 3)))

        return int(num_plants)

    return 0


def validate_response(response: dict) -> bool:
    '''Return True if a response is valid'''
    if not all(response.get(k, False) for k in REQUIRED_FIELDS):
        LOGGER.warning("response %s is missing required fields", response)
        return False
    return True


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


async def fetch_all_plants(num_plants: int) -> list:
    '''Fetch data for all plant endpoints asynchronously'''
    async with aiohttp.ClientSession() as session:

        tasks = []
        plant_id = 0
        not_found_streak = 0

        while len(tasks) < num_plants:

            task = get_plant_data(session, plant_id)

            if task is not None:
                not_found_streak = 0
                tasks.append(task)
            else:
                not_found_streak += 1

            plant_id += 1

        results = await asyncio.gather(*tasks)
        return [result for result in results if result]


def extract() -> list[dict]:
    '''Return a list of dictionaries with the extracted data'''
    timer = perf_counter()
    num_plants = get_num_plants()

    plant_data = asyncio.run(fetch_all_plants(num_plants))

    LOGGER.info("Retrieved plant data. Time taken: %s",
                str(round(perf_counter()-timer, 3)))

    if plant_data:
        return plant_data
    return []


if __name__ == "__main__":
    logger_setup("log_extract.log", "logs")
    data = extract()
    print(data)
