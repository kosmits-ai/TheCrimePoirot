# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables to avoid Python creating .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash appuser
# Set the working directory
WORKDIR /app

# Copy requirements file first (better for Docker layer caching)
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Change ownership of the app directory to the non-root user
RUN mkdir -p /app/repos && chown -R appuser:appuser /app/repos

# Switch to the non-root user
USER appuser

# Expose the Flask app port
EXPOSE 5003

# Run the Flask app
CMD ["python", "app.py"]
