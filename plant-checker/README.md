# LMNH Plant Health Checker
This folder contains the code used to check the health of the plants on display at the LMNH museum.

## Setup

#### To Run locally:
1. Create a venv:
```bash
python -m venv venv
source venv/bin/activate

```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with the following variables:
    - AWS_ACCESS_KEY - AWS pemkey credential
    - AWS_SECRET_ACCESS_KEY - AWS secret pemkey credentials
    - HOST - Database host address
    - DB_PORT - Port for database (1433 for RDS running SQL server)
    - DB_NAME - Name of database (Current schema it is `plants`)
    - DB_PW - Password for accessing RDS
    - DB_USER - Username for accessing RDS
    - TO - Email address of recipient 
    - FROM - Email address of sender

#### To Run as an AWS Lambda:
1. Create an ECR repository through terraform or the AWS UI.
In order for your provisioned architecture one must dockerise their scripts and dependencies and push to an ECR repository.  
For the next steps you will require AWS credentials and the ECR URI.

2. Download the aws-cli:
```bash
brew install awscli
```
3. Verify your credentials:
```bash
aws configure
```
This will require sensitive information to be entered through the command line

4. Verify credentials for specific ECR repository:
```bash
aws ecr get-login-password --region {REGION}| docker login --username AWS --password-stdin {ECR_URI}
```
5. Build your docker image
```bash
docker build -t {image-name} . --platform "linux/amd64"
```
6. Tag your docker image
```bash
docker tag {IMAGE_NAME}:latest {ECR_URI}:latest
```
7. Push docker image to the ECR repository
```bash
docker push {ECR_URI}:latest
```
8. Follow the terraform setup steps in the `../terraform` folder to provision an lambda based off this docker image

## Usage
1. To run locally use the following command:
```bash
python main.py
```
## How it works
#### `main.py`
- Uses `pyodbc` to query the RDS `plants` database to find plants that have had three consecutive readings outside of the accepted range
- Uses `boto3` to send an email via SES to the chosen recipient containing the queried plant ids