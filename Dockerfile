FROM python:3.10-buster

COPY ./profiling/requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
