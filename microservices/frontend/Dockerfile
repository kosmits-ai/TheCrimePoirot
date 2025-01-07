# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt ./  

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application (excluding images folder since it's bind-mounted)
COPY . . 

# Expose port for Streamlit app
EXPOSE 8501

# Define the command to run Streamlit app
CMD ["streamlit", "run", "app.py"]
