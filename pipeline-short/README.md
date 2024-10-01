# Short-Term Data Storage Pipeline

## Setup

1. `python3 -m venv venv` to create a virtual environment.

2. `source venv/bin/activate` to activate the virtual environment.

3. `pip install -r requirements.txt` to install needed requirements.

4. Configure environment `.env` as below.

```sh
DB_HOST=XXXXX
DB_PORT=XXXXX         
DB_NAME=XXXXX           
DB_USER=XXXXX          
DB_PASSWORD=XXXXX
```

## Files

1. `extract.py` connects to the API and pull the data from the endpoints. 

2. `transform.py` transforms and cleans the extracted data.

