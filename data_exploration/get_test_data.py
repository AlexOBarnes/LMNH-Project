'''Running this script produces a csv file containing the LMNH plant data for available plants.'''
import requests
import pandas as pd
import json
import datetime

BASE_URL = "https://data-eng-plants-api.herokuapp.com"
MAX_NOT_FOUND_STREAK = 5


def get_url(id: int):
    '''Gets the API url'''
    url = f"{BASE_URL}/plants/{id}"
    return url


def get_num_plants() -> int:
    '''Return the number of plants on display.'''
    response = requests.get(BASE_URL, timeout=10).json()

    if response.get("success", False):
        return int(response["plants_on_display"])

    return 0


def get_results(response: dict):
    return {
        "plant_id": response.get("plant_id"),
        "botanist_email": response.get("botanist", {"email": None}).get("email"),
        "botanist_name": response.get("botanist", {"name": None}).get("name"),
        "botanist_phone": response.get("botanist", {"phone": None}).get("phone"),
        "images_license_url": response.get("images", {"license_url": None}).get("license_url"),
        "last_watered": response.get("last_watered"),
        "name": response.get("name"),
        "scientific_name": response.get("scientific_name"),
        "origin_location": response.get("origin_location"),
        "soil_moisture": response.get("soil_moisture"),
        "temperature": response.get("temperature"),
        "recording_taken": response.get("recording_taken")
    }


if __name__ == "__main__":
    data = []
    num_found = 0

    num_expected = get_num_plants()

    i = 0
    not_found_streak = 0
    while True:

        if num_found == num_expected:
            break

        url = get_url(i)

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            not_found_streak = 0
            num_found += 1
            try:
                data.append(get_results(response.json()))

            except Exception as err:
                print(err)
        else:
            not_found_streak += 1
            print(response.json())

        if not_found_streak >= MAX_NOT_FOUND_STREAK:
            print("Exceeded not found streak")
            break

        i += 1

    pd.DataFrame(data).to_csv(f"{datetime.datetime.now()}_results.csv")
