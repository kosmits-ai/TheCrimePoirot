#!/bin/bash

# List of microservices and their directories
services=(
    "mongodb"
    "gitleaks"
    "guarddog"
    "safety"
    "bearer"
    "calculate_percentile"
    "api_gateway"
)

# Start each service in the background
for service in "${services[@]}"; do
    echo "Starting $service..."
    (cd $service && python app.py > ../logs/$service.log 2>&1 &) # Navigate and start the service
done

echo "All services started. Logs are saved in the 'logs' directory."
