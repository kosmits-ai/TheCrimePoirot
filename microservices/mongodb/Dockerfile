# Use an official Python image as the base
FROM python:3.12-slim

# Create a non-root user
RUN useradd -ms /bin/bash appuser
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

RUN mkdir -p /app/repos && chown -R appuser:appuser /app/repos
# Expose the port that the service will run on
EXPOSE 5000

# Run the Flask application when the container starts
CMD ["python", "app.py"]
