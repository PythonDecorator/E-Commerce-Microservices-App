FROM python:3.9

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt
COPY app /app
WORKDIR /app
