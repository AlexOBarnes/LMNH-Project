'''Running this script produces a csv file containing the LMNH plant data for available plants.'''
import datetime
import requests as req
import pandas as pd
BASE_URL = "https://data-eng-plants-api.herokuapp.com"


def get_url(plant_id: int):
    '''Gets the API url'''
    return f"{BASE_URL}/plants/{plant_id}"


def get_num_plants() -> int:
    '''Return the number of plants on display.'''
    res= req.get(BASE_URL, timeout=10).json()
    if res.get("success", False):
        return int(res["plants_on_display"])
    return 0


def get_results(res: dict):
    '''Returns the key information from the API response'''
    return {
        "plant_id": res.get("plant_id"),
        "botanist_email": res.get("botanist", {"email": None}).get("email"),
        "botanist_name": res.get("botanist", {"name": None}).get("name"),
        "botanist_phone": res.get("botanist", {"phone": None}).get("phone"),
        "images_license_url": res.get("images", {"license_url": None}).get("license_url"),
        "last_watered": res.get("last_watered"),
        "name": res.get("name"),
        "scientific_name": res.get("scientific_name"),
        "origin_location": res.get("origin_location"),
        "soil_moisture": res.get("soil_moisture"),
        "temperature": res.get("temperature"),
        "recording_taken": res.get("recording_taken")
    }


if __name__ == "__main__":
    data = []
    found = 0
    expected = get_num_plants()
    i = 0
    while True:

        if found == expected:
            break

        response = req.get(get_url(i), timeout=10)

        if response.status_code == 200:
            found += 1
            print(i)
            try:
                data.append(get_results(response.json()))

            except Exception as err:
                print(err)

        i += 1

    pd.DataFrame(data).to_csv(f"{datetime.datetime.now()}_results.csv")
