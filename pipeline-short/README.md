# Short-Term Data Storage Pipeline

## Setup

1. `python3 -m venv venv` to create a virtual environment.

2. `source venv/bin/activate` to activate the virtual environment.

3. Configure environment `.env` as below.

```sh
DB_HOST=XXXXX
DB_PORT=XXXXX         
DB_NAME=XXXXX           
DB_USER=XXXXX          
DB_PASSWORD=XXXXX
```

5. In order to connect to the Microsoft SQL server,

```sh
brew install FreeTDS
export CFLAGS="-I$(brew --prefix openssl)/include"
export LDFLAGS="-L$(brew --prefix openssl)/lib -L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
pip install --pre --no-binary :all: -r requirements.txt --no-cache
```

## Files

1. `extract.py` connects to the API and pull the data from the endpoints. 

2. `transform.py` transforms and cleans the extracted data.

