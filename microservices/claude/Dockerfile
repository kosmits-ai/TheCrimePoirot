FROM python:3.12-slim

# Install required dependencies: git and curl
RUN apt-get update && apt-get install -y git curl \
    && rm -rf /var/lib/apt/lists/*
# Set the working directory
WORKDIR /app

# Copy application dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
# Default command
CMD ["python", "app.py"]