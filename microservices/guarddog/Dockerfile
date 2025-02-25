FROM python:3.12-slim

RUN apt-get update && apt-get install -y git curl

# Create a non-root user
RUN useradd -ms /bin/bash appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .


# Change ownership of the app directory to the non-root user
RUN mkdir -p /app/repos && chown -R appuser:appuser /app/repos

# Switch to the non-root user
USER appuser

EXPOSE 5002

CMD ["python", "app.py"]