FROM python:3.9-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application
COPY . /code

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
CMD ["python", "app.py"] 