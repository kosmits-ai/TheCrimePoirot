# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt ./  

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application (excluding images folder since it's bind-mounted)
COPY . . 

# Change ownership of the app directory to the non-root user
RUN mkdir -p /app/repos && chown -R appuser:appuser /app/repos

# Switch to the non-root user
USER appuser

# Expose port for Streamlit app
EXPOSE 8501

# Define the command to run Streamlit app
CMD ["streamlit", "run", "app.py"]
