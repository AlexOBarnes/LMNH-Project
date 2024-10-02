FROM python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY extract.py .

CMD [ "python", "extract.py" ]