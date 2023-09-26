# Use a base image of Python
FROM python:3.9-slim

# Set environment variables for Python 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the script to the working directory
COPY src/redis_listener.py /app/

# Install the necessary Python packages
RUN pip install redis==3.5.3

# The command that will run when the container starts
CMD ["python", "/app/redis_listener.py"]
