# Short-Term Data Storage Pipeline

## Setup: Running locally

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

### Building a docker image 


### Docker


## Files

1. `extract_short.py` connects to the API and pull the data from the endpoints. 

2. `transform_short.py` transforms and cleans the extracted data.

3. `load_short.py` loads the extracted data into the RDS

4. `pipeline_short.py` contains the lambda handler.
