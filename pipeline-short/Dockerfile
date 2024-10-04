FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt 


COPY extract_short.py .
COPY database_functions.py .
COPY transform_short.py .
COPY load_short.py .
COPY logger.py . 
COPY pipeline_short.py . 

RUN mkdir -p logs
COPY logs/ ./logs

CMD [ "pipeline_short.lambda_handler" ]