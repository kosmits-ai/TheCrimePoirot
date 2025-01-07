# Start from a Python base image
FROM python:3.12-slim

# Install required dependencies: git and curl
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Bearer CLI
RUN curl -sfL https://raw.githubusercontent.com/Bearer/bearer/main/contrib/install.sh | sh

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt . 

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose the port that Flask will run on
EXPOSE 5004

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run Flask on container start
CMD ["flask", "run", "--host=0.0.0.0", "--port=5004"]
