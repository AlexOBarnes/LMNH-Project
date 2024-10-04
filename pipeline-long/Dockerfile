FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pipeline_long.py .
COPY extract_long.py .
COPY transform_long.py .
COPY load_long.py .
COPY logging_long.py .
COPY send_email.py .

CMD [ "pipeline_long.lambda_handler" ]