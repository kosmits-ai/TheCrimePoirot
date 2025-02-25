# Start from a Python base image
FROM python:3.12-slim

# Install required dependencies: git and curl
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Bearer CLI
RUN curl -sfL https://raw.githubusercontent.com/Bearer/bearer/main/contrib/install.sh | sh

# Create a non-root user
RUN useradd -ms /bin/bash appuser
# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt . 

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Change ownership of the app directory to the non-root user
RUN mkdir -p /app/repos && chown -R appuser:appuser /app/repos

# Switch to the non-root user
USER appuser

# Expose the port that Flask will run on
EXPOSE 5004


# Run Flask on container start
CMD ["python", "app.py"]
