# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN useradd -ms /bin/bash appuser

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Change ownership of the app directory to the non-root user
RUN mkdir -p /app/repos && chown -R appuser:appuser /app/

# Switch to the non-root user
USER appuser

# Expose the port Flask will run on
EXPOSE 5008

# Run the Flask app when the container launches
CMD ["python", "app.py"]
