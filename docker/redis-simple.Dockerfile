FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install redis==5.0.0

WORKDIR /app

COPY src/redis_listener.py /app/
COPY src/redis_publisher.py /app/
