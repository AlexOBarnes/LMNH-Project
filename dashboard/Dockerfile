FROM python:latest

WORKDIR /dashboard

RUN mkdir pages

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY dashboard.py .
COPY sl_queries.py .
COPY pages/about.py ./pages
COPY pages/plants.py ./pages

CMD ["streamlit", "run", "dashboard.py","--server.port=8501"]