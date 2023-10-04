FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install redis==5.0.0 bytewax==0.17.1

WORKDIR /app
COPY src/dataflow_echo.py /app/
COPY src/bytewax_redis_input.py /app/
COPY src/dataflow_mobile_counts.py /app/

