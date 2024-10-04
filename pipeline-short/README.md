# LMNH Data Pipeline (short-term storage)

## Setup: Running locally

Ensure that an SQL server RDS has been setup prior and is accessible. 

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

5. To run the pipeline locally, use `python3 pipeline_short.py`

## Setup: Dockerizing and Running on AWS 

1.`brew install awscli`
2. `aws configure`
3. `aws ecr get-login-password --region {REGION}| docker login --username AWS --password-stdin {ECR_URI}`
4. `docker build -t {image-name} . --platform "linux/amd64"`
5. `docker tag {IMAGE_NAME}:latest {ECR_URI}:latest`
6. `docker push {ECR_URI}:latest`


## Files

1. `extract_short.py` connects to the API and pull the data from the endpoints. 

2. `transform_short.py` transforms and cleans the extracted data.

3. `load_short.py` loads the extracted data into the RDS

4. `pipeline_short.py` contains the lambda handler.
