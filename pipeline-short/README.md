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

In order to connect to the Microsoft SQL server, you'll need to have a `ODBC Driver 17 for SQL Server` installed. Use the below commands (on a Mac OS) to do this:

```sh
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17
brew install unixodbc
```

## Files

1. `extract.py` connects to the API and pull the data from the endpoints. 

2. `transform.py` transforms and cleans the extracted data.

