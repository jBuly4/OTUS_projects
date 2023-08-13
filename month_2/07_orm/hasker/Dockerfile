FROM ubuntu:latest
FROM python:3.10.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /hasker

RUN pip install --upgrade pip
COPY requirements.txt /hasker/
RUN pip install -r requirements.txt
COPY . /hasker/
RUN chmod 777 /hasker/hasker_start.sh