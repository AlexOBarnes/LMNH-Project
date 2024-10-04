# LMNH Data Generation & Exploration
This folder contains python scripts that can be used to populate your RDS database and to extract sample data and store as a local CSV for further data exploration.

## Setup
1. Create a venv
```bash
python -m venv venv
source venv/bin/activate
```
2. Install requirements
```bash
pip install -r requirements.txt
```
3. Create a `.env` file containing the following:
    - `BUCKET` - S3 bucket for long term storage
    - `AWS_ACCESS_KEY` - Key used to access AWS
    - `AWS_SECRET_ACCESS_KEY` - Private key used to access AWS
    - `HOST` - Endpoint of database
    - `DB_PORT` - Port of database
    - `DB_NAME` - Name of database
    - `DB_PW` - Password used to access database
    - `DB_USER` - Username used to access database
## Usage
1. To create a local csv file:
```bash
python get_test_data.py
```
2. To populate your RDS/local database use the following command:
```bash
python generate_test_data.py
```
Use the flags `-r` or `--rows` to specify how many rows of data you would like to add
Use the flags `-d` to direct the data to a database; default is the S3 bucket

## How it works
#### get_test_data.py
- Uses `requests` library to get data from plants endpoints
- Uses `pandas` to process the data and convert to a csv
- Uses `datatime` for naming the file created
#### generate_test_data.py
- Parses command line arguments for `--rows` and `--database` using `argparse` library
- Uses the `random` library to generate test data for each column of the recording database
- Uses `pyodbc` to enter this data into the specified database
- `boto3` and `io` libraries are used to upload the generated csv that was generated using the `pandas` library