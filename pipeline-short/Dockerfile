FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

WORKDIR /app 

COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY extract_short.py .
COPY database_functions.py .
COPY transform_short.py .
COPY load_short.py .
COPY logger.py . 
COPY pipeline_short.py . 

CMD [ "pipeline_short.lambda_handler" ]