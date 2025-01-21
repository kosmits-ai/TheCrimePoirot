FROM python:3.12-slim

# Install required dependencies: git and curl
RUN apt-get update && apt-get install -y git curl \
    && rm -rf /var/lib/apt/lists/*

# Install gitleaks
RUN curl -sSL https://github.com/zricethezav/gitleaks/releases/download/v8.21.2/gitleaks_8.21.2_linux_x64.tar.gz | tar -xz -C /usr/local/bin

ENV GITLEAKS_PATH="/usr/local/bin/gitleaks"

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Set the working directory
WORKDIR /app

# Copy application dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership of the app directory to the non-root user
RUN mkdir -p /app/repos && chown -R appuser:appuser /app/repos

# Switch to the non-root user
USER appuser

# Expose the application port
EXPOSE 5001

# Default command
CMD ["python", "app.py"]
