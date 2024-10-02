# LMNH Data Pipeline (Long-Term Storage)
An ETL pipeline that extracts data from a SQL server AWS RDS instance, transforms the data to a CSV and finally loads that data in an S3 bucket.  
In the process the recordings table of the `plants` database is truncated ready for further insertions.

## Setup
1. Ensure that an SQL server RDS has been setup prior and is accessible
    - Note: be sure to store the credentials for accessing this database safely.

### To Run Locally:
2. Setup a venv and install the requirements
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Create a `.env` file with the following:
    - DB_HOST - to access your RDS instance
    - DB_USER - username for accessing RDS
    - DB_PASSWORD - password for accessing RDS
    - DB_NAME - the name of your database, the database name we use is `plants`
        - Note: if you choose a different name be sure to change this in the bash scripts and schema files

### To Run on AWS:

2. Create an ECR repository through terraform or the AWS UI.
In order for your provisioned architecture one must dockerise their scripts and dependencies and push to an ECR repository.  
For the next steps you will require AWS credentials and the ECR URI.

3. Download the aws-cli:
```bash
brew install awscli
```
4. Verify your credentials:
```bash
aws configure
```
This will require sensitive information to be entered through the command line

5. Verify credentials for specific ECR repository:
```bash
aws ecr get-login-password --region {REGION}| docker login --username AWS --password-stdin {ECR_URI}
```
6. Build your docker image
```bash
docker build -t {image-name} . --platform "linux/amd64"
```
7. Tag your docker image
```bash
docker tag {IMAGE_NAME}:latest {ECR_URI}:latest
```
8. Push docker image to the ECR repository
```bash
docker push {ECR_URI}:latest
```
9. Follow the terraform setup steps in the `../terraform` folder to provision an lambda based off this docker image

## Usage
- To use locally one can use the following command:
```bash
python pipeline.py
```
It is a good idea to ensure that the pipeline works with your credentials prior to provisioning the AWS architecture

- To run tests run the following command:
```bash
pytest
```
Alternatively to run specific tests or test files:
```bash
pytest path/to/test_file.py
pytest path/to/test_file.py::test_function_name
```

## How it works