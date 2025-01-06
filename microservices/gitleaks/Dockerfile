FROM python:3.12-slim

# Install required dependencies: git and curl
RUN apt-get update && apt-get install -y git curl

# Install gitleaks
RUN curl -sSL https://github.com/zricethezav/gitleaks/releases/download/v8.21.2/gitleaks_8.21.2_linux_x64.tar.gz | tar -xz -C /usr/local/bin

ENV GITLEAKS_PATH="/usr/local/bin/gitleaks"

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
