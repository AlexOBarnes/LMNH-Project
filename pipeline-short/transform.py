'''Transfroms the extracted data'''
import re
import pandas as pd


def is_valid_email(email: str) -> bool:
    '''Returns True if an email is valid'''
    return (isinstance(email, str)) and ("@" in email)


def split_name(name: str) -> list[str]:
    '''Return the first and last name'''

    names = name.split(" ")
    if len(names) > 1:
        return [names[0], " ".join(names[1:])]
    else:
        return [name, ""]


def split_data(plant_data: dict) -> dict[dict]:
    '''Splits the plant data into dictionaries for different tables'''
    return {"botanist": get_botanist_data(plant_data["botanist"]), "plant": get_plant_data(plant_data)}


def get_plant_data(plant_dict: dict):
    '''Gets plant data, including validation'''


def get_last_watered(last_watered_entry: str | None) -> bool:
    '''Given the last_watered entry, return the last_watered value to be input into the database.'''


def get_botanist_data(botanist_data: dict) -> dict | None:
    '''Formats the extracted json into botanist data. Returns None if a required field is missing.'''
    email = botanist_data.get("email", None)
    full_name = botanist_data.get("name", None)
    if not full_name:
        return None

    names = split_name(full_name)

    return {
        "botanist_email": email if is_valid_email(email) else None,
        "botanist_first_name": names[0],
        "botanist_last_name": names[1],
        "botanist_phone": botanist_data.get("phone", None)
    }


def load_data_into_df(data: list[dict]):
    '''Loads the data into a dataframe'''
