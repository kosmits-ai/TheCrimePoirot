FROM python:3.12-slim

RUN apt-get update && apt-get install -y git curl

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5005

CMD ["python", "app.py"]